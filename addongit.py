'''
Title: addongit
Version: 1.1
Author: Robert Jackson (rmjackson 'at' gmail 'dot' com)
Date: 01.17.2011
Summary:
  Handles setting up my addons repo and cloning/updating to the local wow install.
'''

import os
import sys
import ConfigParser
import shutil
import tempfile
import unicodedata
import logging
from optparse import OptionParser
import tarfile

def extract_archive(tarfile_path, dest_dir):
  '''
  extracts the provided tar to the current directory
  '''
  if not os.path.exists(dest_dir) and not os.path.isdir(dest_dir):
    os.makedirs(dest_dir)
  os.chdir(dest_dir)
  tar = tarfile.open(tarfile_path)
  # Used in python 2.6
  #tar.extractall()
    
  # Hack for 2.4
  for tarinfo in tar:
    tar.extract(tarinfo)
  tar.close()


def get_app_info():
  # determine if application is a script file or frozen exe
  application = {'path': './', 'dir': './', 'start': None}
  if hasattr(sys, 'frozen'):
    application['path'] = sys.executable
    application['start'] = 'start %s --clean-up' % sys.executable
    application['dir'] = os.path.dirname(sys.executable)
    application['type'] = 'binary'
  else:
    application['path'] = os.path.abspath(sys.argv[:1][0])
    application['dir'] = sys.path[0]
    application['start'] = 'python %s --clean-up' % os.path.abspath(sys.argv[:1][0])
    application['type'] = 'python'
  return application

wow_reg = {
            'wow_key_path': 'SOFTWARE\\Wow6432Node\\Blizzard Entertainment\\World of Warcraft',
            'key': None,
            'wow_registry_keys': 0
          }

app_runtime = get_app_info()
          
app_settings = {
               'os': os.name,
               'config_name': os.path.join(app_runtime['dir'], 'addongit.cfg'),
               'launcher_path': None,
               'wow_interface_base': None,
               'remote_repo': None,
               'remote_branch': 'master',
               'addon_base': 'AddOns',
               'config_base_name': None,
               'launch_wow': False,
               'addon_path': None,
               'config_path': None,
               'base_dir': app_runtime['dir'],
               'version': None,
               'name': 'addongit'
             }
             
log_settings = {
               'path': os.path.join(app_runtime['dir'], 'log'),
               'level': 'info',
               'app_name': 'addongit'
               }

cfg = {
      'wow_interface_base': None,
      'addon_base': None,
      'launch_wow': None,
      'log_path': None,
      'log_level': None,
      'remote_branch': None
      }
      
LOG_LEVELS = {
             'debug': logging.DEBUG,
             'info': logging.INFO,
             'warning': logging.WARNING,
             'error': logging.ERROR,
             'critical': logging.CRITICAL
             }

def init_config():
  c = ConfigParser.ConfigParser()
  c.optionxform = str
  return c

config = init_config()
wreg = None

def app_up2date(config_path, local_version):
  log = logging.getLogger()
  log.info('Checking for application update')
  print('Checking for application update')
  log.debug('app_up2date(%s, %s)' % (config_path, local_version))
  config_name = os.path.join(config_path, 'config')
  log.debug('Using %s' % config_name)
  c = init_config()
  if os.path.exists(config_name):
    try:
      c.read(config_name)
      remote_version = c.get('app', 'version')
      log.debug('Local version: %s' % local_version)
      log.debug('Remote version: %s' % remote_version)
      if remote_version != local_version:
        log.info('Application update available. Restarting.')
        print 'Application update available. Restarting.'
        return False
    except Exception, e:
      print str(e)
      log.debug('%s could not be read' % config_name)
      log.error('Unable to determine if update is available.')
      print 'Unable to determine if update is available.'
  return True

def create_log_handle(log_path, log_level, app_name):
  global LOG_LEVELS
  level = LOG_LEVELS.get(log_level, logging.NOTSET)
  if not os.path.exists(log_path): os.makedirs(log_path)
  log_file = os.path.join(log_path, '%s.log' % app_name)
  logging.basicConfig(filename=log_file, filemode='w')
  logger = logging.getLogger()
  logger.setLevel(level)
  logger.info('Initializing %s' % app_name)
  return logger

def get_config_base_name():
  return raw_input('\nEnter the name of the config directory specific to your repo. \
                    \nThis identifies the repo as yours when the updater runs. \
                    \n\n(EX: .nzeer): ')
  
def get_wow_base():
  return raw_input('\nEnter the full path to your WoW Interface directory: ')

def get_remote_repo():
  return raw_input('\nEnter the full address to the remote repo. \
                    \n\n(EX: git://github.com/nzeer/Addons.git): ')

def rebase_local_addons(addon_path, wow_interface_base):
  log = logging.getLogger()
  log.debug('rebase_local_addons(%s, %s)' % (addon_path, wow_interface_base))
  os.chdir(wow_interface_base)
  log.info('Existing AddOns directory located.')
  log.info('Rebasing addons.')
  print 'Existing AddOns directory located.\nRebasing addons.'
  unique_path = '%s.%s' % (addon_path, os.path.basename(tempfile.mktemp()))
  log.debug('Rebasing addons to %s' % unique_path)
  os.rename(addon_path, unique_path)
  print 'Previous directory now located at (%s).' % unique_path
  os.makedirs(addon_path)
  print 'Rebase complete'
  log.info('Rebase complete')
  
def init_git(addon_path, remote_repo, config_path, branch='master'):
  log = logging.getLogger()
  log.debug('init_git(%s, %s, %s, %s)' % (addon_path, remote_repo, config_path, branch))
  print 'Initializing git repo'
  log.info('Initializing git repo')
  log.debug('Initializing git repo (%s) %s in %s' % (branch, remote_repo, addon_path))
  assert os.path.exists(addon_path)
  os.chdir(addon_path)
  log.debug('cd %s' % addon_path)
  
  cmd_git_clone = 'git clone -b %s %s .' % (branch, remote_repo)
  cmd_attrib_set_hidden = 'attrib +h %s' % config_path
  
  os.system(cmd_git_clone)
  os.system(cmd_attrib_set_hidden)
  
  log.debug(cmd_git_clone)
  log.debug(cmd_attrib_set_hidden)
  
  log.info('Repo init complete')
  print 'Repo init complete'
  
def get_reg_handle(key_path):
  log = logging.getLogger()
  log.debug('get_reg_handle(%s)' % key_path)
  global wreg
  return wreg.OpenKey(wreg.HKEY_LOCAL_MACHINE, key_path)
  
def is_initial_run(config_path, git_path):
  log = logging.getLogger()
  log.debug('is_initial_run(%s, %s)' % (config_path, git_path))
  git_exists = os.path.exists(git_path)
  config_exists = os.path.exists(config_path)
  
  log.debug('%s exists: %s' % (config_path, str(config_exists)))
  log.debug('%s exists: %s' % (git_path, str(git_exists)))
  
  # Cleaner, though unorthodox, method or reading this.
  if git_exists and config_exists: 
    log.debug('Not initial run.')
    return False
  log.debug('Initial run.')
  return True
  
def init_wow(launcher_path):
  log = logging.getLogger()
  log.debug('init_wow(%s)' % launcher_path)
  assert os.path.exists(launcher_path)
  log.debug('Launching %s' % launcher_path)
  print 'Launching WoW'
  log.info('Launching WoW')
  os.system('start %s' % (launcher_path))
  
def update(addon_path, branch='master'):
  log = logging.getLogger()
  log.debug('update(%s, %s)' % (addon_path, branch))
  os.chdir(addon_path)
  log.debug('cd %s' % addon_path)
  print 'Updating addons'
  log.info('Updating addons')
  log.debug('Running git pull origin %s from %s' % (branch, addon_path))
  os.system('git pull origin %s' % branch)
  log.debug('git pull complete.')
    
def config_defaults():
  log = logging.getLogger()
  global cfg
  global app_settings
  global config

  try:
    cfg['remote_branch'] = config.get('remote', 'branch')
  except Exception, e:
    log.error(str(e))
    pass

  try:
    cfg['wow_interface_base'] = config.get('local', 'wow_interface_directory')
  except Exception, e:
    log.error(str(e))
    pass
    
  try:
    cfg['addon_base'] = config.get('local', 'addon_path')
  except Exception, e:
    log.error(str(e))
    pass

  try:
    cfg['launch_wow'] = config.getboolean('local', 'launch_wow')
  except Exception, e:
    log.error(str(e))
    pass
    
  # Override defaults where necessary.
  app_settings['wow_interface_base'] = cfg['wow_interface_base'] if cfg['wow_interface_base'] is not None else app_settings['wow_interface_base']
  app_settings['addon_base'] = cfg['addon_base'] if cfg['addon_base'] is not None else app_settings['addon_base']
  app_settings['launch_wow'] = cfg['launch_wow'] if cfg['launch_wow'] is not None else app_settings['launch_wow']
  app_settings['remote_branch'] = cfg['remote_branch'] if cfg['remote_branch'] is not None else app_settings['remote_branch']
  
  # make sure our path is correctly formed with no trailing slashes incase
  # we need to perform some voodoo  
  app_settings['addon_path'] = os.path.normpath(os.path.join(app_settings['wow_interface_base'], app_settings['addon_base']))
  app_settings['config_path'] = os.path.join(app_settings['addon_path'], app_settings['config_base_name'])
  app_settings['git_path'] = os.path.join(app_settings['addon_path'], '.git')

def log_dict(d, name):
  log = logging.getLogger()
  log.debug('Using the following %s: ' % name)
  for k, v in d.iteritems():
    log.debug('\t\t%s: %s' % (k, v))
  log.debug('*' * 10)
  
def config_log():
  global log_settings
  global cfg
  global config
  
  try:
    cfg['log_path'] = config.get('log', 'path')
  except Exception, e:
    pass
    
  try:
    cfg['log_level'] = config.get('log', 'level')
  except Exception, e:
    pass
    
  log_settings['path'] = cfg['log_path'] if cfg['log_path'] is not None else log_settings['path']
  log_settings['level'] = cfg['log_level'] if cfg['log_level'] is not None else log_settings['level']
  
def config_win_reg():
  log = logging.getLogger()
  global app_settings
  global win_reg
  global wreg
  
  # Grabs the WoW install path and launcher path from the registry, and sets defaults.
  # Sets up default for addon directory.

  wow_reg['key'] = get_reg_handle(wow_reg['wow_key_path'])
  if wow_reg['key']: 
    '''tuple: ( An integer giving the number of sub keys this key has., 
        An integer giving the number of values this key has.
        A long integer giving when the key was last modified (if available) as 100's of nanoseconds since Jan 1, 1600. )
    '''
    try:
      wow_reg['wow_registry_keys'] = wreg.QueryInfoKey(wow_reg['key'])[1]
      log.debug('Found %s key(s).' % (wow_reg['wow_registry_keys']))
      if wow_reg['wow_registry_keys'] > 0:
        log.debug('Registry keys detected.')
        app_settings['wow_base'] = wreg.QueryValueEx(wow_reg['key'], 'InstallPath')[0].encode('utf-8')
        app_settings['launcher_path'] = wreg.QueryValueEx(wow_reg['key'], 'GamePath')[0].encode('utf-8')
        
      log_dict(wow_reg, 'registry settings')
    except Exception, e:
      print str(e)
      log.error(str(e))
    else:
      wow_reg['key'].Close()
  
def clean_up():
  global config
  global app_settings
  global log_settings
  global cfg
  global wow_reg
  
  logging.shutdown()
  
  del config
  del app_settings
  del log_settings
  del cfg
  del wow_reg

  

# Begin main app
def main(options=[], args=[]):
  global config
  global app_settings
  global log_settings
  global cfg
  global wreg
  log = None
  
  try:
    config.read(app_settings['config_name'])
  except Exception, e:
    print str(e)
    print 'Continuing without configuration file.'
  
  config_log()
  
  try:
    log = create_log_handle(log_settings['path'], log_settings['level'], log_settings['app_name'])
  except Exception, e:
    print str(e)
    # Something is wrong.
    # Disable logging by setting to a null handler.
    log = logging.getLogger()
    print 'Disabling logging'
  
  log.debug('main(options=%s, args=%s)' % (options, args))
  log.debug('OS is %s' % (app_settings['os']))
    
  if app_settings['os'] == 'nt':
    import _winreg as wreg
    try:
      config_win_reg()
    except Exception, e:
      print str(e)
      log.error(str(e))
      
  elif app_settings['os'] == 'posix':
    # TODO: determine how to handle looking up OSX/linux default install paths'
    pass
  else:
    pass
    
  try:
    config.read(app_settings['config_name'])
    app_settings['version'] = config.get('local', 'version')
    app_settings['remote_repo'] = config.get('remote', 'repo')
  except Exception, e:
    print str(e)
    log.error(str(e))
    # Config not found or cannot be read, grabbing information the hard way.
    app_settings['remote_repo'] = get_remote_repo()
    
  try:
    app_settings['config_base_name'] = config.get('local', 'config_base_name')
  except Exception, e:
    print str(e)
    log.error(str(e))
    # Config not found or cannot be read, grabbing information the hard way.
    app_settings['config_base_name'] = get_config_base_name()

  config_defaults()

  log_dict(app_settings, 'application settings')
    
  log_dict(log_settings, 'log settings')

  # make sure there's a valid repo to talk to.
  assert app_settings['remote_repo'] is not None
  
  new_version_path = '%s.new' % app_settings['base_dir']
  '''
  if options.clean_up:
    shutil.rmtree(new_version_path)
  
  if options.update:
    
    tarfile_path = os.path.join(app_settings['config_path'], '%s-%s.tar.bz2' % (app_settings['name'], options.new_version))
    backup_path = '%s.old' % app_settings['base_dir']
    new_version_path = '%s.new' % app_settings['base_dir']
    
    if os.path.exists(new_version_path): 
      shutil.rmtree(new_version_path)
    extract_archive(tarfile_path, new_version_path)
    #if os.path.exists(backup_path):
      #shutil.rmtree(backup_path)
    #shutil.copytree(app_settings['base_dir'], backup_path)
    #shutil.move(new_version_path, app_settings['base_dir'])
    #os.system(app_runtime['start'])
    #shutil.copy(new_version_path, app_settings['base_dir'])
    
    if app_runtime['type'] == 'python':
      app_up = os.path.join(new_version_path, 'addongit_up.py')
      os.system('python %s --backup-path=%s --new-version-path=%s --current-version-path=%s --app-start-cmd=%s' %
                (app_up, backup_path, new_version_path, app_runtime['dir'], app_runtime['start']))
    elif app_runtime['type'] == 'binary':
      app_up = os.path.join(new_version_path, 'addongit_up.exe')
      os.system('start %s --backup-path=%s --new-version-path=%s --current-version-path=%s --app-start-cmd=%s' %
                (app_up, backup_path, new_version_path, app_runtime['dir'], app_runtime['start']))
    sys.exit()
  
  # Check for application update
  if not app_up2date(app_settings['config_path'], app_settings['version']):
    print 'app not up2date'
    pass
    # Restart 
  '''  
  # is the proposed addon path valid
  # if not, create it.
  if not os.path.exists(app_settings['addon_path']):
    log.info('%s not found' % app_settings['addon_path'])
    # is wow installed
    assert os.path.exists(app_settings['wow_interface_base'])
    log.debug('%s found' % app_settings['wow_interface_base'])
    print 'AddOns directory not found.'
    print 'Creating'
    os.makedirs(app_settings['addon_path'])
    init_git(app_settings['addon_path'], app_settings['remote_repo'], app_settings['config_path'], app_settings['remote_branch'])

  # if its not our repo rebase addons and init
  elif is_initial_run(app_settings['config_path'], app_settings['git_path']):
    # Either the path didnt exist and we've created it
    # or it was the initial run and we've rebased previous addon collection
    rebase_local_addons(app_settings['addon_path'], app_settings['wow_interface_base'])
    
    # Verify that our AddOn path is where it should be before continuing.
    init_git(app_settings['addon_path'], app_settings['remote_repo'], app_settings['config_path'], app_settings['remote_branch'])
  else:
    try:
      update(app_settings['addon_path'], app_settings['remote_branch'])
    except Exception, e:
      print str(e)
      log.error(str(e))
      log.debug('git pull failed.')
      print 'Correcting'
      log.debug('Rebasing addons and initializing git')
      rebase_local_addons(app_settings['addon_path'], app_settings['wow_interface_base'])
      init_git(app_settings['addon_path'], app_settings['remote_repo'], app_settings['config_path'], app_settings['remote_branch'])
    print 'Done.'
    
  if app_settings['launch_wow']: init_wow(app_settings['launcher_path'])
  log.info('Done')
  log.info('==============================================')
  clean_up()
  sys.exit('Finished.')
  
if __name__ == '__main__':

  def getOpts():
    '''
    Setup our cmdline variables.
    '''
    _parser = OptionParser(usage = "usage: %prog [options]")
    
    _parser.add_option('--update', 
                          action='store_true', 
                          default=False, 
                          dest='update', 
                          help='Application update mode.')
    
    _parser.add_option('--clean-up', 
                          action='store_true', 
                          default=False, 
                          dest='clean_up', 
                          help='Called after application update.')
                          
    _parser.add_option('--new-version',
                       action='store', 
                       type='string',
                       default=None,
                       dest='new_version',
                       help='New version')
                       
    (_opts, _args) = _parser.parse_args()
    return _opts, _args

  opts, args = getOpts()
  main(opts, args)
