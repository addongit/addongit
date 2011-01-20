import sys
import os
import shutil
from optparse import OptionParser

def main(opts=[], args=[]):
  
  backup_path = opts.backup_path
  new_version_path = opts.new_version_path
  current_version_path = opts.current_version_path
  app_start_cmd = opts.app_start_cmd
  
  #if os.path.exists(new_path): 
  #    shutil.rmtree(new_path)
  #extract_archive(tarfile_path, new_path)
  if os.path.exists(backup_path):
    shutil.rmtree(backup_path)
  os.renames(current_version_path, backup_path)
  
  try:
    #for file in os.listdir(new_version_path):
      #shutil.copy(file, current_version_path)
    shutil.copytree(new_version_path, current_version_path)
  except Exception, e:
    print str(e)
    
  os.system('%s --clean-up' % app_start_cmd)
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