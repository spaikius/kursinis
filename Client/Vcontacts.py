import logging
import socket
import tempfile
import json
import hashlib
import re

from collections import defaultdict

from pymol import cmd
from pymol.cgo import *
from pymol import stored

python3 = sys.version_info >= (3,0)

__author__  = "Rimvydas Noreika"
__credits__ = ["Justas Dapkūnas"]
__version__ = "1.0.1"
__status__  = "Development"


def Vcontacts(
    # Selectors
    leftSelector='', rightSelector='',
    # Left side positive filters
    chainLeftIn='',resiNumLeftIn='',resiNameLeftIn='',atomSerialLeftIn='',
    atomNameLeftIn='',
    # Left side negative filters
    chainLeftOut='',resiNumLeftOut='',resiNameLeftOut='', atomSerialLeftOut='',
    atomNameLeftOut='',
    # Right side positive filters
    chainRightIn='',resiNumRightIn='',resiNameRightIn='',atomSerialRightIn='',
    atomNameRightIn='',
    # Right side negative filters
    chainRightOut='',resiNumRightOut='',resiNameRightOut='',atomSerialRightOut='',
    atomNameRightOut='',
    # Contact Area
    contactAreaMin='',contactAreaMax='',
    # Minimal distance
    minimalDistanceMin='',minimalDistanceMax='',
    # Sequence separation
    seqSeparationMin='',seqSeparationMax='',
    # Misc.
    model='', solvent='False', color='white', invert='False', opacity='1',
    # Server connection
    host='127.0.0.1', port='8888',
    # Debug mode
    debug='False'
    ):
    """
DESCRIPTION
    Vcontacts -


IMPORTANT
    ALL CALCULATIONS ARE MADE IN LOCAL SERVER
    DEPENDECIES: server.py, voronota executable

USAGE
    Vcontacts [ leftSelect [, rightSelect [, chainLeftIn [, resiNumLeftIn 
              [, resiNameLeftIn [, atomSerialLeftIn [, atomNameLeftIn 
              [, chainLeftOut [, resiNumLeftOut [, resiNameLeftOut 
              [, atomSerialLeftOut [, atomNameLeftOut [, chainRightIn 
              [, resiNumRightIn [, resiNameRightIn [, atomSerialRightIn 
              [, atomNameRightIn [, chainRightOut [, resiNumRightOut 
              [, resiNameRightOut [, atomSerialRightOut [, atomNameRightOut
              [, contactAreaMin [, contactAreaMax [, minimalDistanceMin 
              [, minimalDistanceMax [, seqSeparationMin [, seqSeparationMax 
              [, model [, solvent [, color [, invert [, opacity [, host 
              [, port [, debug 
              ]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]

PARAMETERS              TYPE     DESCRIPTION
    model               String   The name of the model       Default: current
    color               String   Color for CGO.              Default: white
    opacity             Float    Opacity for CGO.            Default: 1.0
    solvent             Boolean  Display solvent contacts.   Default: False
    invert              Boolean  Reverse query.              Default: False

PARAMETERS-QUERY
    chainLeftIn         String   Selection for first contacting group
    resiNumLeftIn       Integer  Selection for first contacting group
    resiNameLeftIn      String   Selection for first contacting group
    atomSerialLeftIn    Integer  Selection for first contacting group
    atomNameLeftIn      String   Selection for first contacting group

    chainLeftOut        String   Negative selection for first contacting group
    resiNumLeftOut      Integer  Negative selection for first contacting group
    resiNameLeftOut     String   Negative selection for first contacting group
    atomSerialLeftOut   Integer  Negative selection for first contacting group
    atomNameLeftOUT     String   Negative selection for first contacting group

    chainRightIn        String   Selection for second contacting group
    resiNumRightIn      Integer  Selection for second contacting group
    resiNameRightIn     String   Selection for second contacting group
    atomSerialRightIn   Integer  Selection for second contacting group
    atomNameRightIn     String   Selection for second contacting group

    chainRightOut       String   Negative selection for second contacting group
    resiNumRightOut     Integer  Negative selection for second contacting group
    resiNameRightOut    String   Negative selection for second contacting group
    atomSerialRightOut  Integer  Negative selection for second contacting group
    atomNameRightOUT    String   Negative selection for second contacting group

    contactAreaMin      Float    Minimum contact area
    contactAreaMax      Float    Minimum contact area
    minimalDistanceMin  Float    Minimal minimum distance
    minimalDistanceMax  Float    Minimal maximum distance
    seqSeparationMin    Float    Minimum residue sequence separation
    seqSeparationMax    Float    Maximum residue sequence separation

    debug               Boolean  Debug mode. default: False

PARAMETERS-CONNECTION
    host                String   Server hostname.    Default localhost
    port                Integer  Server port number. Default 8888

EXAMPLE

    Vcontacts color=#FFFF00, chainLeftIn=A C, resiNumLeftOut=20:50

VCONTACTS                       2019-05-31
    """

    # Logger level
    logging_level = logging.INFO if not Bool(debug) else logging.DEBUG

    # Init logger
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging_level)

    # Loggin error wrapper
    logging.parser_error = CallCounter(logging.error)

    # Get model from  selectors
    sele_model = get_selectors_model(leftSelector, rightSelector)

    if sele_model:
        model = sele_model
    else:
        model = get_model(model)

    params = params_parser(solvent, color, invert, opacity)

    if logging.parser_error.counter != 0:
        return

    # Append atom serials
    atomSerialLeftIn  = atomSerialLeftIn  + get_serials(leftSelector)
    atomSerialRightIn = atomSerialRightIn + get_serials(rightSelector)

    # Compose query commands
    Vfilter = compose(
        # Left side positive filters
        chainLeftIn, resiNumLeftIn, resiNameLeftIn, atomSerialLeftIn,
        atomNameLeftIn,
        # Left side negative filters
        chainLeftOut, resiNumLeftOut, resiNameLeftOut,  atomSerialLeftOut,
        atomNameLeftOut,
        # Right side positive filters
        chainRightIn, resiNumRightIn, resiNameRightIn, atomSerialRightIn,
        atomNameRightIn,
        # Right side negative filters
        chainRightOut, resiNumRightOut, resiNameRightOut, atomSerialRightOut,
        atomNameRightOut,
        # Contact Area
        contactAreaMin, contactAreaMax,
        # Minimal distance
        minimalDistanceMin, minimalDistanceMax,
        # Sequence separation
        seqSeparationMin, seqSeparationMax
        )


    query = json.dumps({
        'filter': Vfilter,
        'params': params
    })

    try:
        # Create TCP client obj
        client = TCPClient(host, port)
        # Start TCP client
        client.start()
    except Exception as e:
        logging.critical(e)
        logging.info('Server might not be running')
        return

    try:
        # Check if server has PDB file
        if not client.check_file(model):
            client.send_file(model)

        cgo_path = client.get_cgo(model, query)

    except socket.timeout as e:
        logging.error("Connection time out.")
        return
    except Exception as e:
        logging.error("Server side error")
        return

    del client

    # draw CGOs
    draw_CGO(cgo_path)

    return


stored._vcontacts_id = 1
cmd.extend('Vcontacts', Vcontacts)
selections_ = lambda: cmd.Shortcut(cmd.get_names('selections'))
cmd.auto_arg[0]['Vcontacts'] = [selections_, 'left side selections', ', ']
cmd.auto_arg[1]['Vcontacts'] = [selections_, 'right side selections', ', ']


class CallCounter:
    """Decorator to determine number of calls for a method"""

    def __init__(self, method):
        self.method = method
        self.counter = 0

    def __call__(self, *args, **kwargs):
        self.counter += 1
        return self.method(*args, **kwargs)


class TimeOutErr(Exception): pass

class TCPClient:
    '''TCP client'''

    # CONSTANTS
    RESP_OK   = 'OK'
    CHECKFILE = 'CHECKFILE '
    SENDFILE  = 'SENDFILE '

    def __init__(self, host, port):
        try:
            self.address = (host, int(port))
        except ValueError:
            raise ValueError("Port number must be numeric.")
        self._bufferSize = 8192
        self._socket = None

    def send(self, request, encode=True):
        if encode:
            self._socket.sendall(request.encode())
        else:
            self._socket.sendall(request)

    def recieve(self, decode=True):
        if decode:
            return self._socket.recv(self._bufferSize).decode()
        return self._socket.recv(self._bufferSize)

    def start(self):
        """Function for initializing client socket and connecting to server"""
        # create socket
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # 10 minutes for timeout
            self._socket.settimeout(600)
        except socket.error as msg:
            logging.error("Can't create socket. Error code: {}, msg: {}".format(*msg))
            raise

        # Open TCP connection
        try:
            self._socket.connect(self.address)
        except socket.error:
            logging.error("Can't connect to the server on {}:{}".format(*self.address))
            raise

    def close(self):
        """Close the TCP connection"""
        # Report server that connection is closed
        self._socket.sendall(''.encode())
        self._socket.close()

    def check_file(self, model):
        fh = get_pdb_file(model)
        fh.seek(0)
        m = hashlib.sha256()

        for chunk in iter(lambda: fh.read(4096), "".encode()):
            m.update(chunk)

        fh.close()

        # Send request CHECKFILE FILENAME CHECHSUM
        self.send(self.CHECKFILE + model + " " + m.hexdigest())

        # Wait for responce
        srv_resp = self._socket.recv(self._bufferSize).decode()

        return True if srv_resp == self.RESP_OK else False

    def send_file(self, model):
        """Sends the file to the server"""

        fh = get_pdb_file(model)
        file_size = fh.tell()
        fh.seek(0)

        # Send request
        request = self.SENDFILE + model + ' ' + str(file_size)
        logging.debug("request {request}")
        self.send(request)

        # Wait for ACK
        srv_resp = self.recieve()

        if srv_resp != self.RESP_OK:
            logging.debug("response {srv_resp}")
            raise Exception('Server refuse to accept file')


        self.send(fh.read(), encode=False)
        fh.close()

        srv_resp = self.recieve()
        if srv_resp != "OK":
            logging.debug("response {srv_resp}")
            raise Exception('Fail after sending file')

    def get_cgo(self, model, query):
        """get_CGO draw data"""
        file_name = model.lower()
        query_len = len(query)

        # Send GETCGO request
        request = "GETCGO " + file_name
        self._socket.sendall(request.encode())

        # Wait for ACK
        srv_resp = self._socket.recv(self._bufferSize).decode()
        if srv_resp.split(" ")[0] != self.RESP_OK:
            raise Exception("Something went wrong...")

        # Send query len
        self._socket.sendall(str(query_len).encode())

        # Wait for ACK
        srv_resp = self._socket.recv(self._bufferSize).decode()
        if srv_resp.split(" ")[0] != 'OK':
            raise Exception("Something went wrong...")

        # Send query
        self._socket.sendall(query.encode())

        # Wait for responce
        srv_resp = self._socket.recv(self._bufferSize).decode()
        srv_resp = srv_resp.split(" ")
        if srv_resp[0] != 'OK':
            raise Exception("Something went wrong...")

        file_size = srv_resp[1]

        # Send file size ACK to server
        self._socket.sendall(file_size.encode())

        bytes_remaining = int(file_size)

        data = ''

        while bytes_remaining != 0:
            if bytes_remaining >= self._bufferSize:
                slab = self._socket.recv(self._bufferSize)
                data += slab.decode()
                sizeof_slab_received = len(slab)
                bytes_remaining -= int(sizeof_slab_received)
            else:
                slab = self._socket.recv(bytes_remaining)
                data += slab.decode()
                sizeof_slab_received = len(slab)
                bytes_remaining -= int(sizeof_slab_received)



        data = json.loads(data)

        summary(data['summary'])

        return data['path']


def params_parser(solvent, color, invert, opacity):
    '''Params parser'''
    _params = {
        'query': dict(),
        'drawing': dict()
    }
    
    if not Bool(solvent):
        _params['query']['--no-solvent'] = True

    if Bool(invert):
        _params['query']['--invert'] = True,

    color = Color(color)
    if color:
        _params['drawing']['--default-color'] = color

    opacity = Float(opacity)
    if 0 <= opacity and opacity >= 1:
       _params['drawing']['--alpha'] = opacity
    else:
        logging.parser_error('Invalid opacity value: {} must be between 0 and 1'.format(opacity)) 

    return _params


# --- START OF PYMOL DEPENDENCIES --- 

def get_pdb_file(model):
    '''Returns temp file_obj handler'''
    tmp_file = tempfile.TemporaryFile()
    tmp_file.write(cmd.get_pdbstr(model).encode())
    return tmp_file


def get_model(model):
    """Get model if not supplied or check if given model exists in pymol"""
    all_models = cmd.get_object_list()

    if len(all_models) == 0:
        logging.parser_error('No models are opened.')
        return

    model = model.lower()

    if model and (model in all_models):
        return model

    if len(all_models) > 1:
        logging.parser_error("Please specify which model you want to use. {}".format(all_models))
        return

    return all_models[0]


def draw_CGO(cgo_path):
    '''Draws CGO'''
    import os.path
    # FIXME:
    if os.path.isfile(cgo_path):
        cmd.run(cgo_path)
    else:
        logging.info("No contacts found for the given query")


def summary(data):
    total = 0
    for chain in data:
        print("Chain: %s Contact area: %.2f" % (chain, data[chain]))
        total += data[chain]
    if total:
        print("Total area: %.2f" % (total))


def get_selectors_model(sele1, sele2):
    Lmodel = get_model_from_selector(sele1)
    Rmodel = get_model_from_selector(sele2)

    if (Lmodel and Rmodel) and (Lmodel != Rmodel):
        logging.parser_error("Models in selectors does not match")
        return None

    return Lmodel


def get_model_from_selector(selector):
    if not selector:
        return None

    if not (selector in cmd.get_names('selections')):
        logging.parser_error("No such selector: {}".format(selector))
        return None

    models = cmd.get_object_list(selector)

    if len(models) > 1:
        logging.parser_error("Selector {} is composed from different models".format(selector))
        return None

    return models[0]


def get_serials(selector):
    if not selector:
        return ''

    atoms_ids = {'atoms_ids': []}
    cmd.iterate(selector, 'atoms_ids.append(ID)', space=atoms_ids)
 
    return ' '.join(compress_atoms(atoms_ids['atoms_ids']))

# --- END OF PYMOL DEPENDENCIES ---

# --- START OF UTILS ---

def compress_atoms(atoms_list):
    '''Returns compressed atoms list
        [1,2,3,4,6,7,90,101,102,103] => ['1:4', '6:7', '90', '101:103']
    '''
    start, prev = None, None
    compressed = list()
    atoms_list.sort()

    for current_id in atoms_list:
        if start is None:
            start = current_id
            continue
        
        if prev is None:
            if start + 1 != current_id:
                compressed.append(str(start))
                start = current_id
            else: 
                prev = current_id
            continue

        if current_id == prev + 1:
            prev = current_id
            continue
        else:
            compressed.append("{0}:{1}".format(start, prev))
            start, prev = current_id, None
    else:
        if prev is not None: compressed.append("{0}:{1}".format(start, prev))
        else:                compressed.append(str(start))
        

    return compressed

# --- END OF UTILS ---

# --- START OF GENERIC TYPES ---

def Bool(arg):
    """Parse string to boolean"""
    return arg.lower() in ('y', 'true', 't', '1')


def Generic(val):
    """Returns Generic value"""
    val = [v.upper() for v in val.split()]
    return ','.join(val).replace(r"/^,+|,+$/gm",'')


def Float(val):
    """Returns float value or empty string if val is not type of float"""
    try:
        return float(val)
    except ValueError:
        return ''


def Int(val):
    """Returns int value or empty string if val is not type of int"""
    try:
        return int(val)
    except ValueError:
        return ''

# --- END OF GENERIC TYPES ---

# --- START OF CUSTOM TYPES ---

def Color(color):
    default_colors = defaultdict(lambda: None,{
        'blue'  : '0000ff',
        'pink'  : 'ff80ed',
        'red'   : 'ff0000',
        'orange': 'ffa500',
        'yellow': 'ffff00',
        'green' : '00ff00',
        'black' : '000000',
        'white' : 'ffffff',
        'grey'  : 'c0c0c0'
    })
    
    _color = default_colors[color.lower()]
    if _color:
        return _color
    else:
        _color = re.match('^(?:#)?([A-Fa-f0-9]{6})$', color)

        if _color:
            return _color.group(0)

        logging.parser_error("Unrecognized color: {}".format(color))

# --- END OF CUSTOM TYPES ---

# --- STAT OF QUERY COMPOSER --
def compose(
    # Left side positive filters
    chainLeftIn,resiNumLeftIn,resiNameLeftIn,atomSerialLeftIn,
    atomNameLeftIn,
    # Left side negative filters
    chainLeftOut,resiNumLeftOut,resiNameLeftOut, atomSerialLeftOut,
    atomNameLeftOut,
    # Right side positive filters
    chainRightIn,resiNumRightIn,resiNameRightIn,atomSerialRightIn,
    atomNameRightIn,
    # Right side negative filters
    chainRightOut,resiNumRightOut,resiNameRightOut,atomSerialRightOut,
    atomNameRightOut,
    # Contact Area
    contactAreaMin,contactAreaMax,
    # Minimal distance
    minimalDistanceMin,minimalDistanceMax,
    # Sequence separation
    seqSeparationMin,seqSeparationMax
    ):
    """For composing query arguments"""

    output=''

    match_first=''
    match_first=append_to_local_output(match_first, 'c', Generic(chainLeftIn))
    match_first=append_to_local_output(match_first, 'r', Generic(resiNumLeftIn))
    match_first=append_to_local_output(match_first, 'a', Generic(atomSerialLeftIn))
    match_first=append_to_local_output(match_first, 'R', Generic(resiNameLeftIn))
    match_first=append_to_local_output(match_first, 'A', Generic(atomNameLeftIn))
    output=append_to_global_output(output, '--match-first', match_first)

    match_first_not=''
    match_first_not=append_to_local_output(match_first_not, 'c', Generic(chainLeftOut))
    match_first_not=append_to_local_output(match_first_not, 'r', Generic(resiNumLeftOut))
    match_first_not=append_to_local_output(match_first_not, 'a', Generic(atomSerialLeftOut))
    match_first_not=append_to_local_output(match_first_not, 'R', Generic(resiNameLeftOut))
    match_first_not=append_to_local_output(match_first_not, 'A', Generic(atomNameLeftOut))
    output=append_to_global_output(output, '--match-first-not', match_first_not)

    match_second=''
    match_second=append_to_local_output(match_second, 'c', Generic(chainRightIn))
    match_second=append_to_local_output(match_second, 'r', Generic(resiNumRightIn))
    match_second=append_to_local_output(match_second, 'a', Generic(atomSerialRightIn))
    match_second=append_to_local_output(match_second, 'R', Generic(resiNameRightIn))
    match_second=append_to_local_output(match_second, 'A', Generic(atomNameRightIn))
    output=append_to_global_output(output, '--match-second', match_second)

    match_second_not=''
    match_second_not=append_to_local_output(match_second_not, 'c', Generic(chainRightOut))
    match_second_not=append_to_local_output(match_second_not, 'r', Generic(resiNumRightOut))
    match_second_not=append_to_local_output(match_second_not, 'a', Generic(atomSerialRightOut))
    match_second_not=append_to_local_output(match_second_not, 'R', Generic(resiNameRightOut))
    match_second_not=append_to_local_output(match_second_not, 'A', Generic(atomNameRightOut))
    output=append_to_global_output(output, '--match-second-not', match_second_not)

    output=append_to_global_output(output, '--match-min-area', Float(contactAreaMin))
    output=append_to_global_output(output, '--match-max-area', Float(contactAreaMax))

    output=append_to_global_output(output, '--match-min-dist', Float(minimalDistanceMin))
    output=append_to_global_output(output, '--match-max-dist', Float(minimalDistanceMax))

    output=append_to_global_output(output, '--match-min-seq-sep', Int(seqSeparationMin))
    output=append_to_global_output(output, '--match-max-seq-sep', Int(seqSeparationMax))

    return output


def get_input_logical_value(val):
    """Returns logical value"""
    logical = '&'.join(val.split()).replace(r"/&+/gm",'&')
    logical = logical.replace(r"/&\|/gm",'|').replace(r"/\|&/gm",'|')
    logical = logical.replace(r"/\|+/gm",'|').replace(r"/^&+|&+$/gm",'')
    logical = logical.replace(r"/^\|+|\|+$/gm",'')
    return logical


def append_to_local_output(main, suffix, value):
    result=main
    if value != '':
        if result != '':
            result+='&'
        result+= suffix + '<' + str(value)+ '>'
    return result


def append_to_global_output(main, suffix, value):
    result=main
    if value != '':
        if result != '':
            result += ' '
        result += suffix + ' \'' + str(value) + '\''
    return result

# --- END OF QUERY COMPOSER --
