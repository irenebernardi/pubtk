import pytest
import os
#from tests.local import Submitlocal
from local import Submitlocal

class TestSubmitLocal(object):
    @pytest.fixture #make setup fixed and shareable among tests
    def submit_setup(self):
        submit=Submitlocal()
        #prepare data for shell script -> serialize keyword args into string of shell commands
        submit.update_templates(label='test', cwd=os.getcwd(), env={}, command='echo "test"')
        return submit

    def test_job (self, submit_setup):
        #through fixture, get instance of SubmitLocal()
        submit = submit_setup

        #serializes kwargs and creates script
        #submit.create_job()
        submit.create_job(cwd=os.getcwd())
        #check shell file exists through path_template attr of Submit()
        assert os.path.exists(submit.path)

        #open shell file in read mode
        with open(submit.path, 'r') as fptr:
            script = fptr.read()
        print(f'script is {script}')
        #assert 'echo "test"' in script
        #check that cd matches the one in update_templates()
        assert 'cd {}'.format(os.getcwd()) in script
        '''# check that script is made with sh shell
        assert '#!/usr/bin/env sh' in script
        #line below less generic
        #assert '#!/bin/sh' in script or '#!/bin/zsh' in script
        assert '#!/usr/bin/env sh' in script
        #check we sourced bash env
       #assert 'source ~/.zshrc' in script TODO fix make if else'''
        #check user's env and if it is in script
        def check_shell():
            return os.environ.get('SHELL', 'Unknown')
        user_shell = check_shell()
        if user_shell == 'sh':
            assert '#!/bin/sh' in script
        elif user_shell == 'zsh':
            assert 'source ~/.zshrc' in script
        else:
            assert '#!/usr/bin/env sh' in script





