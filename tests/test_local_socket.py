import pytest
import os
from pubtk.runtk.dispatchers import Dispatcher, SFS_Dispatcher, INET_Dispatcher
from pubtk.runtk.submit import Submit, SGESubmitINET, SGESubmitSFS
from pubtk.runtk.runners import HPCRunner
from pubtk.utils import get_exports, get_port_info
import logging
import json
from local import Submitlocal

logger = logging.getLogger('test')
# logger records events at info level and higher : everything except debug
logger.setLevel(logging.INFO)
# set output of log
handler = logging.FileHandler('localtest_job.log')

formatter = logging.Formatter('>>> %(asctime)s --- %(funcName)s --- %(levelname)s >>>\n%(message)s <<<\n')
handler.setFormatter(formatter)
logger.addHandler(handler)

class TestLocalSubmit(object):
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
        dispatcher = dispatcher_setup
        dispatcher.create_job() #create_job is Submit method
        #check that shell script was created
        assert os.path.exists(dispatcher.shellfile)
        dispatcher.socketname = f'{dispatcher.sockname[0]},{dispatcher.sockname[1]}'



        ### logger: records events that happen as program runs at INFO level and above
        # log env variables of dispatcher object and convert to JSON formatted string
        logger.info("dispatcher.env:\n{}".format(json.dumps(dispatcher.env)))
        # log the socket name of the dispatcher object (convert to string for display)
        logger.info("dispatcher.sockname:\n{}".format(dispatcher.sockname))
        # log shellfile of dispatcher object (convert to string for display)
        logger.info("dispatcher.shellfile:\n{}".format(dispatcher.shellfile))

        # open the shell file in read mode and idsplay in terminal
        with open(dispatcher.shellfile, 'r') as fptr:
            script = fptr.read()
        print(script) #display on terminal, although line below also saves it to localtest_job.log
        logger.info('script: \n{}'.format(script))
        # log the port that the dispatcher is listening to (socket is tuple of address and port)
        # line below too many values to unpack
        #logger.info("port info (dispatcher listen):\n{}".format(get_port_info(dispatcher.sockname[1])))
        # not enough values
        #ogger.info("port info (dispatcher listen):\n{}".format(get_port_info(dispatcher.sockname)))
        # test_local_socket.py
        #logger.info("port info (dispatcher listen):\n{}".format(get_port_info(f'{dispatcher.sockname[0]},{dispatcher.sockname[1]}')))
        #logger.info("runner.socketname: IP={}, Port={}".format(*runner.socketname))

        #command in dispatcher_setup
        #assert 'echo "test"' in script
        # parse shell file to extract env variables
        env = get_exports(dispatcher.shellfile)
        #determine that env actually contains right env variables  before creating HPC runner oject
        print(f'env is {env}')
        #log shellfile env variables in log output
        logger.info(env)
        # select runner with shellfile env variables
        #runner = HPCRunner(env=env)
        runner = HPCRunner(env=env, socketname=dispatcher.sockname)
        #log which socket name is used by runner
        print(f'socket is  {runner.socketname}')
        logger.info("runner.socketname:\n{}".format(runner.socketname))
        #HPCRunner method, establishes socket connection between Dispatcher and Runner
        runner.connect()
        #accept new connection: block and wait for new client, reject other clients if connected
        connection, peer_address = dispatcher.accept()


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
        assert runner.mappings['strvalue'] == '1'
        assert runner.mappings['intvalue'] == 2
        assert runner.mappings['fltvalue'] == 3.0
        logger.info("port info (dispatcher clean):\n{}".format(get_port_info(dispatcher.sockname[1])))

