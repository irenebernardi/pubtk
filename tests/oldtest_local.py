'''import pytest
import os
from pubtk.runtk.dispatchers import Dispatcher, SFS_Dispatcher, INET_Dispatcher, SH_Dispatcher
from pubtk.runtk.submit import Submit, SGESubmitINET, SGESubmitSFS'''
from local import Submitlocal
'''from pubtk.runtk.runners import HPCRunner, Runner
from pubtk.utils import get_exports, get_port_info
import logging
import json
'''
import pytest
import os
from pubtk.runtk.dispatchers import Dispatcher, SFS_Dispatcher, INET_Dispatcher
from pubtk.runtk.submit import Submit, SGESubmitINET, SGESubmitSFS
from pubtk.runtk.runners import Runner, HPCRunner
from pubtk.utils import get_exports, get_port_info
import logging
import json


logger = logging.getLogger('test')
logger.setLevel(logging.INFO)
handler = logging.FileHandler('test_job.log')

formatter = logging.Formatter('>>> %(asctime)s --- %(funcName)s --- %(levelname)s >>>\n%(message)s <<<\n')
handler.setFormatter(formatter)
logger.addHandler(handler)

class TestLocalSubmit(object):
    #this breaks pytest
    '''def __init__(self, socket):
        self.socket = socket'''

    @pytest.fixture
    def dispatcher_setup(self):

        dispatcher = INET_Dispatcher(cwd=os.getcwd(),
                                   submit=Submitlocal(),
                                   gid='localrun')
        dispatcher.update_env({'strvalue': '1',
                               'intvalue': 2,
                               'fltvalue': 3.0})
        dispatcher.submit.update_templates(command='echo "test"')
        return dispatcher


    def test_job(self, dispatcher_setup):
        #self.socket = None
        dispatcher = dispatcher_setup
        dispatcher.create_job() #create_job method is part of Submit class
        assert os.path.exists(dispatcher.shellfile) #check that shell script was created
        logger.info("dispatcher.env:\n{}".format(json.dumps(dispatcher.env)))
        logger.info("dispatcher.sockname:\n{}".format(dispatcher.sockname))
        logger.info("dispatcher.shellfile:\n{}".format(dispatcher.shellfile))
        with open(dispatcher.shellfile, 'r') as fptr:
            script = fptr.read()
        logger.info("script:\n{}".format(script))
        assert 'echo "test"' in script
        env = get_exports(dispatcher.shellfile)

        '''
        env = get_exports(dispatcher.shellfile)
        env['socketname'] = self.socket  # Add 'socketname' to 'env'
        runner = Runner(env=env)  # Now 'socketname' is part of 'env'
        logger.info("runner.socketname:\n{}".format(runner.socketname))  # This should work now
         '''
        '''# get env variables
        env = get_exports(dispatcher.shellfile)
        env['socketname'] = env['SOCNAME']
        #env['connect'] = Runner.connect TODO figure out why sometimes works sometimes doesnt

        #TODO ASK why no connect instance for regular runner?

        # NOW RUNNING WITHOUT CONNECT TO SEE IF FINE WITH REGULAR RUNNER
        logger.info(env)
        runner = HPCRunner(env=env)
        logger.info("runner.socketname:\n{}".format(runner.socketname))
        #runner.connect()
        connection, peer_address = dispatcher.accept()
        logger.info("port info (runner connect):\n{}".format(get_port_info(dispatcher.sockname[1])))
        logger.info("runner.host_socket:\n{}".format(runner.host_socket))
        test_message = 'runner -> dispatcher message'
        runner.send(test_message)
        recv_message = dispatcher.recv()
        assert test_message == recv_message
        runner.connect()
        connection, peer_address = dispatcher.accept()
        logger.info("runner.host_socket:\n{}".format(runner.host_socket))
        test_message = 'runner -> dispatcher message'
        runner.send(test_message)
        recv_message = dispatcher.recv()
        assert test_message == recv_message
        logger.info("""\
runner -> dispatcher message:
runner sent                  ---> dispatcher recv
{} ---> {}""".format(test_message, recv_message))
        test_message = 'dispatcher -> runner message'
        dispatcher.send(test_message)
        recv_message = runner.recv()
        logger.info("""\
dispatcher -> runner message:
dispatcher sent              ---> runner recv
{} ---> {}""".format(test_message, recv_message))
        assert test_message == recv_message
        runner.close()
        dispatcher.clean()
        logger.info("runner.mappings:\n{}".format(json.dumps(runner.mappings)))
        assert runner.mappings['strvalue'] == '1'
        assert runner.mappings['intvalue'] == 2
        assert runner.mappings['fltvalue'] == 3.0
        logger.info("port info (dispatcher clean):\n{}".format(get_port_info(dispatcher.sockname[1])))'''


        env = get_exports(dispatcher.shellfile)


        logger.info(env)
        runner = HPCRunner(env=env)
        logger.info("runner.socketname:\n{}".format(runner.socketname))
        runner.connect()
        connection, peer_address = dispatcher.accept()
        logger.info("runner.mappings after connecting:\n{}".format(runner.mappings))
        logger.info("port info (runner connect):\n{}".format(get_port_info(dispatcher.sockname[1])))
        logger.info("runner.host_socket:\n{}".format(runner.host_socket))
        test_message = 'runner -> dispatcher message'
        runner.send(test_message)
        recv_message = dispatcher.recv()
        assert test_message == recv_message
        logger.info("""\
        runner -> dispatcher message:
        runner sent                  ---> dispatcher recv
        {} ---> {}""".format(test_message, recv_message))
        test_message = 'dispatcher -> runner message'
        dispatcher.send(test_message)
        recv_message = runner.recv()
        logger.info("""\
        dispatcher -> runner message:
        dispatcher sent              ---> runner recv
        {} ---> {}""".format(test_message, recv_message))
        assert test_message == recv_message
        runner.close()
        logger.info("port info (runner close):\n{}".format(get_port_info(dispatcher.sockname[1])))
        dispatcher.clean()
        logger.info("runner.mappings:\n{}".format(json.dumps(runner.mappings)))
        #assert runner.mappings['strvalue'] == '1'
        # Add this line before the failing assert
        print("Keys in runner.mappings:", runner.mappings.keys())

        # Modify the assert statement to use .get() with a default value

        assert runner.mappings.get('strvalue', None) == '1'
        assert runner.mappings['intvalue'] == 2
        assert runner.mappings['fltvalue'] == 3.0
        logger.info("port info (dispatcher clean):\n{}".format(get_port_info(dispatcher.sockname[1])))

