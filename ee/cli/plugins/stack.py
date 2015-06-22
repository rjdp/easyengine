"""Stack Plugin for EasyEngine."""

from cement.core.controller import CementBaseController, expose
from cement.core import handler, hook
from ee.core.aptget import EEAptGet
from ee.core.download import EEDownload
from ee.core.shellexec import EEShellExec
from ee.core.fileutils import EEFileUtils
from ee.core.apt_repo import EERepo
from ee.core.extract import EEExtract
from ee.core.mysql import EEMysql
from ee.core.addswap import EESwap
from ee.core.git import EEGit
from ee.core.checkfqdn import check_fqdn
from pynginxconfig import NginxConfig
from ee.core.services import EEService
import random
import string
import configparser
import time
import shutil
import os
import pwd
import grp
import codecs
import platform
from ee.cli.plugins.stack_services import EEStackStatusController
from ee.cli.plugins.stack_migrate import EEStackMigrateController
from ee.cli.plugins.stack_upgrade import EEStackUpgradeController
from ee.cli.plugins.nginxstack import EENginxStack
from ee.cli.plugins.phpstack import EEPhpStack
from ee.cli.plugins.mysqlstack import EEMysqlStack
from ee.cli.plugins.hhvmstack import EEHhvmStack
from ee.cli.plugins.adminstack import EEAdminStack
from ee.cli.plugins.postfixstack import EEPostfixStack
from ee.cli.plugins.mailstack import EEMailStack
from ee.cli.plugins.mailscannerstack import EEMailScannerStack
from ee.core.variables import EEVariables
from ee.core.logging import Log

def ee_stack_hook(app):
    # do something with the ``app`` object here.
    pass


class EEStackController(CementBaseController):
    class Meta:
        label = 'stack'
        stacked_on = 'base'
        stacked_type = 'nested'
        description = 'Stack command manages stack operations'
        arguments = [
            (['--all'],
                dict(help='Install all stack', action='store_true')),
            (['--web'],
                dict(help='Install web stack', action='store_true')),
            (['--admin'],
                dict(help='Install admin tools stack', action='store_true')),
            (['--mail'],
                dict(help='Install mail server stack', action='store_true')),
            (['--mailscanner'],
                dict(help='Install mail scanner stack', action='store_true')),
            (['--nginx'],
                dict(help='Install Nginx stack', action='store_true')),
            (['--php'],
                dict(help='Install PHP stack', action='store_true')),
            (['--mysql'],
                dict(help='Install MySQL stack', action='store_true')),
            (['--hhvm'],
                dict(help='Install HHVM stack', action='store_true')),
            (['--postfix'],
                dict(help='Install Postfix stack', action='store_true')),
            (['--wpcli'],
                dict(help='Install WPCLI stack', action='store_true')),
            (['--phpmyadmin'],
                dict(help='Install PHPMyAdmin stack', action='store_true')),
            (['--adminer'],
                dict(help='Install Adminer stack', action='store_true')),
            (['--utils'],
                dict(help='Install Utils stack', action='store_true')),
            ]
        usage = "ee stack (command) [options]"

    @expose(hide=True)
    def default(self):
        """default action of ee stack command"""
        from ee.cli.plugins.adminstack import EEAdminStack
        EEAdminStack(package_dict=EEVariables.ee_admin).install_stack()
        self.app.args.print_help()
        #EEAdminStack(self).purge_stack()


    @expose(help="Install packages")
    def install(self, packages=[], apt_packages=[], disp_msg=True):
        """Start installation of packages"""
        self.msg = []

        # Default action for stack installation
        if ((not self.app.pargs.web) and (not self.app.pargs.admin) and
           (not self.app.pargs.mail) and (not self.app.pargs.nginx) and
           (not self.app.pargs.php) and (not self.app.pargs.mysql) and
           (not self.app.pargs.postfix) and (not self.app.pargs.wpcli) and
           (not self.app.pargs.phpmyadmin) and (not self.app.pargs.hhvm)
           and
           (not self.app.pargs.adminer) and (not self.app.pargs.utils) and
           (not self.app.pargs.mailscanner) and (not self.app.pargs.all)):
            # self.app.pargs.web = True
            # self.app.pargs.admin = True
            pass

        if self.app.pargs.all:
            self.app.pargs.web = True
            self.app.pargs.admin = True
            self.app.pargs.mail = True

        if self.app.pargs.web:
            EEMysqlStack().install_stack()
            EENginxStack().install_stack()
            EEPhpStack().install_stack()
            EEHhvmStack().install_stack()
            EEAdminStack(package_dict=EEVariables.ee_wpclistack).install_stack()
            EEPostfixStack().install_stack()

        if self.app.pargs.admin:
            EEAdminStack(package_dict=EEVariables.ee_admin).install_stack()

        if self.app.pargs.mail:
            EEMailStack(package_dict=EEVariables.ee_webmailstack, apt_packages=EEVariables.ee_mail).install_stack()

        if self.app.pargs.nginx:
           EENginxStack().install_stack()


        if self.app.pargs.php:
            EEPhpStack().install_stack()


        if self.app.pargs.hhvm:
            EEHhvmStack().install_stack()

        if self.app.pargs.mysql:
            EEMysqlStack().install_stack()

        if self.app.pargs.postfix:
            EEPostfixStack().install_stack()

        if self.app.pargs.wpcli:
            EEAdminStack(package_dict=EEVariables.ee_wpclistack).install_stack()

        if self.app.pargs.phpmyadmin:
            EEAdminStack(package_dict=EEVariables.ee_phpmyadminstack).install_stack()

        if self.app.pargs.adminer:
            EEAdminStack(package_dict=EEVariables.ee_adminerstack).install_stack()

        if self.app.pargs.mailscanner:
            EEMailScannerStack().install_stack()

        if self.app.pargs.utils:
            EEAdminStack(package_dict=EEVariables.ee_utils).install_stack()

        for res in hook.run('stack_install_hook', self.app):
            # do something with res... 
            pass

        # Hook for stack install plugin
        # hook.run('stack_install_hook', self.app)


    @expose(help="Remove packages")
    def remove(self):
        """Start removal of packages"""

        # Default action for stack remove
        if ((not self.app.pargs.web) and (not self.app.pargs.admin) and
           (not self.app.pargs.mail) and (not self.app.pargs.nginx) and
           (not self.app.pargs.php) and (not self.app.pargs.mysql) and
           (not self.app.pargs.postfix) and (not self.app.pargs.wpcli) and
           (not self.app.pargs.phpmyadmin) and (not self.app.pargs.hhvm) and
           (not self.app.pargs.adminer) and (not self.app.pargs.utils) and
           (not self.app.pargs.mailscanner) and (not self.app.pargs.all)):
            # self.app.pargs.web = True
            # self.app.pargs.admin = True
            pass

        if self.app.pargs.all:
            self.app.pargs.web = True
            self.app.pargs.admin = True
            self.app.pargs.mail = True

        if self.app.pargs.web:
            EEMysqlStack().remove_stack()
            EENginxStack().remove_stack()
            EEPhpStack().remove_stack()
            EEHhvmStack().remove_stack()
            EEAdminStack(package_dict=EEVariables.ee_wpclistack).remove_stack()
            EEPostfixStack().remove_stack()

        if self.app.pargs.admin:
            EEAdminStack(package_dict=EEVariables.ee_admin).remove_stack()

        if self.app.pargs.mail:
            EEMailStack(package_dict=EEVariables.ee_webmailstack, apt_packages=EEVariables.ee_mail).remove_stack()

        if self.app.pargs.nginx:
           EENginxStack().remove_stack()


        if self.app.pargs.php:
            EEPhpStack().remove_stack()


        if self.app.pargs.hhvm:
            EEHhvmStack().remove_stack()

        if self.app.pargs.mysql:
            EEMysqlStack().remove_stack()

        if self.app.pargs.postfix:
            EEPostfixStack().remove_stack()

        if self.app.pargs.wpcli:
            EEAdminStack(package_dict=EEVariables.ee_wpclistack).remove_stack()

        if self.app.pargs.phpmyadmin:
            EEAdminStack(package_dict=EEVariables.ee_phpmyadminstack).remove_stack()

        if self.app.pargs.adminer:
            EEAdminStack(package_dict=EEVariables.ee_adminerstack).remove_stack()

        if self.app.pargs.mailscanner:
            EEMailScannerStack().remove_stack()

        if self.app.pargs.utils:
            EEAdminStack(package_dict=EEVariables.ee_utils).remove_stack()

        # Hook for stack remove plugins
        for res in hook.run('stack_remove_hook', self.app):
            # do something with res... 
            pass
            # print("Hook Return Value > %s" % res)
        # hook.run('stack_remove_hook', self.app)


    @expose(help="Purge packages")
    def purge(self):
        """Start purging of packages"""
        # Default action for stack purge
        if ((not self.app.pargs.web) and (not self.app.pargs.admin) and
           (not self.app.pargs.mail) and (not self.app.pargs.nginx) and
           (not self.app.pargs.php) and (not self.app.pargs.mysql) and
           (not self.app.pargs.postfix) and (not self.app.pargs.wpcli) and
           (not self.app.pargs.phpmyadmin) and (not self.app.pargs.hhvm) and
           (not self.app.pargs.adminer) and (not self.app.pargs.utils) and
           (not self.app.pargs.mailscanner) and (not self.app.pargs.all)):
            self.app.pargs.web = True
            self.app.pargs.admin = True

        if self.app.pargs.all:
            self.app.pargs.web = True
            self.app.pargs.admin = True
            self.app.pargs.mail = True

        if self.app.pargs.web:
            EEMysqlStack().purge_stack()
            EENginxStack().purge_stack()
            EEPhpStack().purge_stack()
            EEHhvmStack().purge_stack()
            EEAdminStack(package_dict=EEVariables.ee_wpclistack).purge_stack()
            EEPostfixStack().purge_stack()

        if self.app.pargs.admin:
            EEAdminStack(package_dict=EEVariables.ee_admin).purge_stack()

        if self.app.pargs.mail:
            EEMailStack(package_dict=EEVariables.ee_webmailstack, apt_packages=EEVariables.ee_mail).purge_stack()

        if self.app.pargs.nginx:
           EENginxStack().purge_stack()


        if self.app.pargs.php:
            EEPhpStack().purge_stack()


        if self.app.pargs.hhvm:
            EEHhvmStack().purge_stack()

        if self.app.pargs.mysql:
            EEMysqlStack().purge_stack()

        if self.app.pargs.postfix:
            EEPostfixStack().purge_stack()

        if self.app.pargs.wpcli:
            EEAdminStack(package_dict=EEVariables.ee_wpclistack).purge_stack()

        if self.app.pargs.phpmyadmin:
            EEAdminStack(package_dict=EEVariables.ee_phpmyadminstack).purge_stack()

        if self.app.pargs.adminer:
            EEAdminStack(package_dict=EEVariables.ee_adminerstack).purge_stack()

        if self.app.pargs.mailscanner:
            EEMailScannerStack().purge_stack()

        if self.app.pargs.utils:
            EEAdminStack(package_dict=EEVariables.ee_utils).purge_stack()


def load(app):
    # register the plugin class.. this only happens if the plugin is enabled
    handler.register(EEStackController)
    handler.register(EEStackStatusController)
    handler.register(EEStackMigrateController)
    handler.register(EEStackUpgradeController)

    # register a hook (function) to run after arguments are parsed.
    hook.register('post_argument_parsing', ee_stack_hook)
