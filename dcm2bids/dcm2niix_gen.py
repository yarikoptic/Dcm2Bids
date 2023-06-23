# -*- coding: utf-8 -*-

"""Dcm2niix class"""

import logging
import os
import shlex
import shutil
from glob import glob

from dcm2bids.utils.utils import DEFAULT, run_shell_command


class Dcm2niixGen(object):
    """ Object to handle dcm2niix execution

    Args:
        dicomDirs (list): A list of folder with dicoms to convert
        bidsDir (str): A path to the root BIDS directory
        participant: Optional Participant object
        options (str): Optional arguments for dcm2niix

    Properties:
        sidecars (list): A list of sidecar path created by dcm2niix
    """

    def __init__(
        self,
        dicomDirs,
        bidsDir,
        participant=None,
        options=DEFAULT.dcm2niixOptions,
        helper=False
    ):
        self.logger = logging.getLogger(__name__)
        self.sidecarsFiles = []
        self.dicomDirs = dicomDirs
        self.bidsDir = bidsDir
        self.participant = participant
        self.options = options
        self.helper = helper

    @property
    def outputDir(self):
        """
        Returns:
            A directory to save all the output files of dcm2niix
        """
        tmpDir = self.participant.prefix if self.participant else DEFAULT.helperDir
        tmpDir = self.bidsDir / DEFAULT.tmpDirName / tmpDir
        if self.helper:
            tmpDir = self.bidsDir
        return tmpDir

    def run(self, force=False, helper=False):
        """ Run dcm2niix if necessary

        Args:
            force (boolean): Forces a cleaning of a previous execution of
                             dcm2niix

        Sets:
            sidecarsFiles (list): A list of sidecar path created by dcm2niix
        """
        try:
            oldOutput = os.listdir(self.outputDir) != []
        except Exception:
            oldOutput = False

        if oldOutput and force:
            self.logger.warning("Previous dcm2niix directory output found:")
            self.logger.warning(self.outputDir)
            self.logger.warning("'force' argument is set to True")
            self.logger.warning("Cleaning the previous directory and running dcm2niix")

            shutil.rmtree(self.outputDir, ignore_errors=True)

            if not os.path.exists(self.outputDir):
                os.makedirs(self.outputDir)

            self.execute()

        elif oldOutput:
            self.logger.warning("Previous dcm2niix directory output found:")
            self.logger.warning(self.outputDir)
            self.logger.warning("Use --force_dcm2niix to rerun dcm2niix \n")

        else:
            if not os.path.exists(self.outputDir):
                os.makedirs(self.outputDir)

            self.execute()

        self.sidecarFiles = glob(os.path.join(self.outputDir, "*.json"))

    def execute(self):
        """ Execute dcm2niix for each directory in dicomDirs
        """
        for dicomDir in self.dicomDirs:
            cmd = ['dcm2niix', *shlex.split(self.options),
                   '-o', self.outputDir, dicomDir]
            output = run_shell_command(cmd)

            try:
                output = output.decode()
            except Exception:
                pass

            self.logger.debug("\n%s", output)
            self.logger.info("Check log file for dcm2niix output")
