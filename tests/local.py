import os
import subprocess
from collections import namedtuple

from pubtk.runtk import SGESubmit


# create a template that runs a shell on personal computer

#new : creating and returning new object ; init is for initializing object state
#__new__ is a static method and param is cls, not self : it only has access to class level data, not instance level data
class Template(object):

    def __new__(cls, template=None, key_args=None, **kwargs): #TODO: ask why set key_args here if defined in __init__
        if isinstance(template, Template):
            return template
        else:
            return super(). __new__(cls)

    def __init__(self, template, key_args = None, **kwargs):
        if isinstance(template, Template):
            return
        # if template not an instance of Template, store it as object attribute:
        self.template = template
        #if key_args is not None, self.kwargs = key_args. If key_args is None, self.kwargs is created w the keys extracted from the template string by the get_args method.
        if key_args:
            self.kwargs ={key: "{" + key + "}" for key in key_args}
        else:
            self.kwargs = {key : "{" + key + "}" for key in self.get_args() }

    #order of method definition does not matter
    def get_args(self):
        #find all characters in self.template that are enclosed in curly braces
        import re
        return re.findall(r'{(.*?)}', self.template)


    def format(self, **kwargs):
        mkwargs = self.kwargs | kwargs
        try:
            return self.template.format(**mkwargs)
        except KeyError as e:
            mkwargs = mkwargs | {key: "{" + key + "}" for key in self.get_args()}
            #return self.template.format(**mkwargs)
            #leave placeholder as is
            return self.template.format_map(mkwargs)

    def update(self, **kwargs):
        self.template = self.format(**kwargs)

    def __repr__(self):
        return self.template

    def __call__(self):
        return self.template

#SERIALIZERS : one key value dict, key is sh, dict is converted into a string w shell commands
serializers = {
    'sh': lambda x: '\nexport ' + '\nexport '.join(['{}="{}"'.format(key, val) for key, val in x.items()])}

def serialize(args, var ='env', serializer ='sh'):
    if var in args and serializer in serializers:
        args[var] = serializers[serializer](args[var])
    return args # not necessary to return




class Submit(object):
    key_args = {'label', 'cwd', 'env'}

    def __init__(self, submit_template, script_template, **kwargs):
        self.submit_template = Template(submit_template)
        self.script_template = Template(script_template)
        self.path_template = Template("{cwd}/{label}.sh", {'cwd', 'label'})
        self.templates = {self.submit_template, self.script_template, self.path_template}
        self.kwargs = self.submit_template.kwargs | self.script_template.kwargs | self.path_template.kwargs
        self.job = None
        self.submit = None
        self.script = None
        self.path = None
        self.handles = None


    def create_job(self, **kwargs):
        kwargs = serialize(kwargs, var = 'env', serializer = 'sh')
        kwargs['cwd'] = os.getcwd()
        #kwargs['sockname'] = ','.join(map(str, kwargs.get('sockname', ('', ''))))
        #kwargs['sockname'] = '{},{}'.format(*kwargs.get('sockname', ('', '')))  # Format sockname as a string
        # Access sockname from kwargs, not from self
        # kwargs['sockname'] = kwargs.get('sockname', '')
        sockname = kwargs.get('sockname', ('', ''))
        kwargs['sockname'] = ','.join(map(str, sockname))
        job = self.format_job(**kwargs)
        self.job = job
        self.submit = job.submit
        self.script = job.script
        self.path = job.path
        fptr = open(self.path, 'w')
        fptr.write(self.script)
        fptr.close()
        print(f"Current working directory: {os.getcwd()}")
        print(f"Template before formatting: {self.script_template}")
        print(f"Formatted script template: {self.script_template.format(**kwargs)}")
    def format_job(self, **kwargs):
        job = namedtuple('job', 'submit script path')
        submit = self.submit_template.format(**kwargs)
        script = self.script_template.format(**kwargs)
        path = self.path_template.format(**kwargs)
        return job(submit, script, path)

    def update_templates(self, **kwargs):
        kwargs = serialize(kwargs, var = 'env', serializer = 'sh')
        for template in self.templates:
            template.update(**kwargs)

    def __repr__(self):
        job = self.format_job()
        reprstr = \
            """\
submit:
----------------------------------------------
{submit}
script:
----------------------------------------------
{script}
----------------------------------------------
""".format(**job._asdict())
        return reprstr

    def submit_job(self):
        self.proc = subprocess.run(self.job.submit.split(' '), text=True, stdout=subprocess.PIPE, \
            stderr=subprocess.PIPE)
        return self.proc


    def __format__(self, template = False, **kwargs): #dunder method, (self, spec)
        template = template or self.script_template
        mkwargs = self.kwargs | kwargs
        return template.format(**mkwargs)

    def create_handles(self, **kwargs):
        # Update handles with sockname as a formatted string
        self.handles.update({'sockname': '{},{}'.format(*kwargs.get('sockname', ('', '')))})
        self.handles.update(kwargs)
        return self.handles


#make class for regular macbook submit

class Submitlocal(Submit): # no cores, no vmem
    script_args = {'label', 'cwd', 'env', 'command', 'socname'}
    # using bash or zsh based on user default shell
    script_template = \
        """\
#!/usr/bin/env sh  
cd {cwd}
# setup environment
#source ~/.zshrct4004 04t[it[ei[pe
# set env variables 
export SOCNAME="{sockname}"
export STRVALUE="{strvalue}"
export INTVALUE="{intvalue}"
export FLTVALUE="{fltvalue}"
#specify command to run file and where to store file output
{command} > {cwd}/{label}.run
"""
    def __init__(self, **kwargs):
        super().__init__(
            # command that submits job
            #submit_template = Template(template="sh {cwd}/{label}.sh", key_args={'cwd', 'label'}),
            submit_template=Template(template="sh {cwd}/{label}.sh {sockname}", key_args={'cwd', 'label', 'sockname'}),
            script_template=Template(self.script_template, key_args=self.script_args))
        self.job_output = None


    def submit_job(self, **kwargs):
        proc = super().submit_job()
        #no job ids locally
        self.job_output = proc.stdout
        return self.job_output




