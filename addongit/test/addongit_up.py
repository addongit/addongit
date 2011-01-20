import sys
import os
import shutil
import logging
from optparse import OptionParser

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
  
app_runtime = get_app_info()

log_settings = {
               'path': os.path.join(app_runtime['dir'], 'log'),
               'level': 'debug',
               'app_name': 'addongit_upgrade'
               }
      
LOG_LEVELS = {
             'debug': logging.DEBUG,
             'info': logging.INFO,
             'warning': logging.WARNING,
             'error': logging.ERROR,
             'critical': logging.CRITICAL
             }

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

def main(opts=[], args=[]):
  global log_settings
  log = None
  
  try:
    log = create_log_handle(log_settings['path'], log_settings['level'], log_settings['app_name'])
  except Exception, e:
    print str(e)
    # Something is wrong.
    # Disable logging by setting to a null handler.
    log = logging.getLogger()
    print 'Disabling logging'
  
  log.debug('main(options=%s, args=%s)' % (opts, args))
  
  log.debug('cwd %s' % os.getcwd())
  os.chdir('..')
  log.debug('cwd %s' % os.getcwd())
  
  backup_path = opts.backup_path
  new_version_path = opts.new_version_path
  current_version_path = opts.current_version_path
  app_start_cmd = opts.app_start_cmd
  
  log.debug('backup: %s' % backup_path)
  log.debug('new: %s' % new_version_path)
  log.debug('current: %s' % current_version_path)
  log.debug('app start: %s' % app_start_cmd)
  
  #if os.path.exists(new_path): 
  #    shutil.rmtree(new_path)
  #extract_archive(tarfile_path, new_path)
  try:
    if os.path.exists(backup_path):
      shutil.rmtree(backup_path)
      log.debug('deleted %s' % backup_path)
  except Exception, e:
    log.error('failed deleting existing backup (%s): %s' % (backup_path, str(e)))
    sys.exit()
    
  #try:
  #  os.renames(current_version_path, backup_path)
  #  log.debug('renamed %s to %s' % (current_version_path, backup_path))
  #except Exception, e:
  #  log.error('failed on renaming current (%s): %s' % (current_version_path, str(e)))
  #  sys.exit()
    
  try:
    #for file in os.listdir(new_version_path):
      #shutil.copy(file, current_version_path)
    shutil.copytree(new_version_path, current_version_path)
    log.debug('copied %s to %s' % (new_version_path, current_version_path))
  except Exception, e:
    log.error('failed copying new (%s): %s' % (new_version_path, str(e)))
    sys.exit()
  
  log.info('Finished upgrading')
  os.popen('%s --clean-up' % app_start_cmd)
  log.debug('Called %s and exiting.' % app_start_cmd)
  sys.exit()
  
if __name__ == '__main__':

  def getOpts():
    '''
    Setup our cmdline variables.
    '''
    _parser = OptionParser(usage = "usage: %prog [options]")
    
    _parser.add_option('--backup-path',
                       action='store', 
                       type='string',
                       default=None,
                       dest='backup_path',
                       help='Backup path')
                       
    _parser.add_option('--new-version-path',
                       action='store', 
                       type='string',
                       default=None,
                       dest='new_version_path',
                       help='New path')
                       
    _parser.add_option('--current-version-path',
                       action='store', 
                       type='string',
                       default=None,
                       dest='current_version_path',
                       help='Current path')
                       
    _parser.add_option('--app-start-cmd',
                       action='store', 
                       type='string',
                       default=None,
                       dest='app_start_cmd',
                       help='Application start cmd')
                       
    (_opts, _args) = _parser.parse_args()
    return _opts, _args

  # TODO: add optparse
  opts, args = getOpts()
  main(opts, args)