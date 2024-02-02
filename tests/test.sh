#!/usr/bin/env sh  
cd {cwd}
# setup environment
#source ~/.zshrc
# set env variables 
export SOCNAME="{sockname}"
export STRVALUE="{strvalue}"
export INTVALUE="{intvalue}"
export FLTVALUE="{fltvalue}"
#specify command to run file and where to store file output
{command} > {cwd}/{label}.run
