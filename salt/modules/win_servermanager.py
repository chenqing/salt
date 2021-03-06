'''
Manage Windows features via the ServerManager powershell module
'''


# Import salt libs
import salt.utils


def __virtual__():
    '''
    Load only on windows
    '''
    if salt.utils.is_windows():
        return 'win_servermanager'
    return False
    

def _srvmgr(func):
    '''
    execture a function from the ServerManager PS module and return the STDOUT
    '''
    
    return __salt__['cmd.run']( 'powershell -InputFormat None -Command "& {{ Import-Module ServerManager ; {0} }}"'.format( func ) )


def _parse_powershell_list(lst):
    '''
    Parse a command output when piped to format-list
    '''
    
    ret = {}
    for line in lst.splitlines():
        if line:
            splt = line.split()
            ret[ splt[0] ] = splt[2]
    
    return ret


def list_available():
    '''
    List available features to install
    '''
    
    return _srvmgr('Get-WindowsFeature -erroraction silentlycontinue')


def list_installed():
    '''
    List available features to install
    '''
    
    ret = {}
    for line in list_available().splitlines()[2:]:
        splt = line.split()
        if splt[0] == '[X]':
            name = splt.pop(-1)
            splt.pop(0)
            display_name = ' '.join(splt)
            ret[name] = display_name
    
    return ret


def install(feature, recurse=False):
    '''
    Install the feature
    
    Note:
    Some features requires reboot after un/installation, if so until the server is restarted
    Other features can not be installed !
    
    Note:
    Some features takes a long time to un/installation, set -t with a long timeout
    '''
    
    sub = ''
    if recurse:
        sub = '-IncludeAllSubFeature'
    out = _srvmgr( 'Add-WindowsFeature -Name {0} {1} -erroraction silentlycontinue | format-list'.format(feature, sub) )
    return _parse_powershell_list( out )


def remove(feature):
    '''
    Remove an installed feature
    
    Note:
    Some features requires reboot after un/installation, if so until the server is restarted
    Other features can not be installed !
    
    Note:
    Some features takes a long time to un/installation, set -t with a long timeout
    '''
    
    out = _srvmgr( 'Remove-WindowsFeature -Name {0} -erroraction silentlycontinue | format-list'.format(feature) )
    return _parse_powershell_list( out )

