'''
Wrapping params from app cell
Useful because it can be hard to predict how the app cell will pass things in,
and to retrieve params in different forms (e.g., CLI vs. prose)
'''
import json

from ..util.debug import dprint
from .globals import Var




class Params:
    '''
    Provides interface for:
    -----------------------
    # Flattened params
    * `[]` access to required params (e.g., essential UPAs, workspace stuff)
    * `get`-like access to default-backed params ( e.g., 3rd-party tool params with defaults)
    * RDP Clsf params in prose mode
    * RDP Clsf params in CLI args mode

    You can leave off non-default params, like you would with underlying CLI tools
    However, if you do pass something in for a param, it has to be valid.

    Use `params.getd` for default-backed params

    Also the parameter groups are an effect of the app cell ui, 
    and params will be flattened right away
    '''

    DEFAULTS = {
       'output_name': None, # null case
       'conf': 0.8,                 
       'gene': 'silva_138_ssu',           
       'minWords': None, # null case
    }

    REQUIRED = [
        'workspace_id',
        'workspace_name',
        'amp_mat_upa',
    ]

    PARAM_GROUPS = [
        'rdp_clsf',
    ]

    CUSTOM = ['silva_138_ssu']


    def __init__(self, params):

        ## Validate params and flattened params
        self._validate(params)

        ## Flatten
        params = self.flatten(params)
        
        ## Custom transformations to internal state ##

        if 'output_name' in params and params['output_name'] == '':
            params['output_name'] = None # treat empty string as null case
                                         # since ui only returns strings for string type
        
        self.params = params


    def _validate(self, params):
        VALID = list(self.DEFAULTS.keys()) + self.REQUIRED + self.PARAM_GROUPS

        for p in params:
            if p not in VALID:
                raise Exception()

        for p in self.flatten(params):
            if p not in VALID:
                raise Exception()


    def is_custom(self) -> bool:
        return self.getd('gene') in self.CUSTOM


    @property
    def prose_args(self) -> dict:
        '''
        For printing all RDP Clsf params to user in a pretty way
        '''

        return {
            'conf': '%g' % self.getd('conf'),
            'gene': self.getd('gene'),
            'minWords': 'default' if self.getd('minWords') is None else str(self.getd('minWords')),
        }


 
    @property
    def cli_args(self) -> list:
        '''
        Non-default RDP Classifier `classify` CLI args
        '''
       
        cli_args = []

        if self.getd('conf') != self.DEFAULTS['conf']:
            cli_args += ['--conf', str(self.getd('conf'))]

        if self.getd('gene') == self.DEFAULTS['gene']:
            cli_args += ['--train_propfile', Var.propfile[self.getd('gene')]]
        else:
            cli_args += ['--gene', self.getd('gene')]

        if self.getd('minWords') != self.DEFAULTS['minWords']:
            cli_args += ['--minWords', str(self.getd('minWords'))]


        return cli_args


    def __getitem__(self, key):
        '''
        For required params (e.g., input UPAs, workspace stuff)
        Should not use this for default-backed params
        as those can be left off params
        so use `getd` for those
        '''
        if key not in self.REQUIRED:
            raise Exception()

        return self.params[key]

    def getd(self, key):
        '''
        For default-backed params (e.g., tunable numbers)
        Like `get`
        Return the user-supplied value, or the default value if none was supplied
        '''
        if key not in self.DEFAULTS:
            raise Exception('`params.getd(x)` only applicable to params with defaults')

        return self.params.get(key, self.DEFAULTS[key])


    def __repr__(self) -> str:
        return 'Wrapper for params:\n%s' % (json.dumps(self.params, indent=4))



    @staticmethod
    def flatten(d):
        '''
        At most 1 level nesting
        '''
        d1 = d.copy()
        for k, v in d.items():
            if isinstance(v, dict):
                for k1, v1 in d1.pop(k).items():
                    d1[k1] = v1
        return d1

