import logging
import socket
import tempfile

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
    leftSelect='', rightSelect='',
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
    model='', solvent='False', color='False', invert='False',
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

USAGE
    Vcontacts model [, solvent [, color [, invert [, chainLeftIn
                    [, resiNumLeftIn [, resiNameLeftIn [, atomSerialLeftIn
                    [, atomNameLeftIn [, chainLeftOut [, resiNumLeftOut
                    [, resiNameLeftOut [, atomSerialLeftOut [, atomNameLeftOUT
                    [, chainRightIn [, resiNumRightIn [, resiNameRightIn
                    [, atomSerialRightIn [, atomNameRightIn [, chainRightOut
                    [, resiNumRightOut [, resiNameRightOut [, atomSerialRightOut
                    [, atomNameRightOUT [, contactAreaMin [, minimalDistanceMin
                    [, seqSeparationMin [, contactAreaMax [, minimalDistanceMax
                    [, seqSeparationMax [, host [, port [, debug
                    ]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]

PARAMETERS              TYPE     DESCRIPTION
    model               String   The name of the model
    solvent             Boolean  Display solvent contacts.   Default: False
    color        Boolean  Use random colors for CGO.  Default: False
    invert             Boolean  Reverse query.              Default: False

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

    Vcontacts 5ara, color=True, chainLeftIn=A C, resiNumLeftOut=20:50

VCONTACTS                       2019-01-05
    """

    # Setup logger
    logging_level = logging.INFO

    if Bool(debug):
        logging_level = logging.DEBUG


    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging_level)

    # Loggin error wrapper
    logging.error = CallCounter(logging.error)

    # Get model from  selectors
    sele_model = get_selectors_model(leftSelect, rightSelect)

    if sele_model:
        model = sele_model
    else:
        model = get_model(model)

    if logging.error.counter != 0:
        return

    # Append atom serials
    atomSerialLeftIn  = atomSerialLeftIn  + get_serials(leftSelect)
    atomSerialRightIn = atomSerialRightIn + get_serials(rightSelect)

    # Compose query commands
    query = compose(
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
        seqSeparationMin,seqSeparationMax,
        # Misc.
        model, solvent, color, invert)

    print(query)
    try:
        # Create TCP client obj
        client = TCPClient(host, port)
        # Start TCP client
        client.start()
    except Exception as e:
        logging.critical("Can't start client. {}".format(e))
        return

    try:
        # Check if server has PDB file
        if not client.check_file(model):
            print("Sending the file...")
            client.send_file(model)
            print("File has been sent")

        print("Fetching CGO file...")

        # GET method returns temp file_obj handler
        cgo_fh = client.get_cgo(model, query)

        # cgo_fh = client.get_cgo(model, query)
        print("Download completed.")
    except socket.timeout as e:
        # logging.error("Connection time out.")
        logging.error("Server side error.")
        return

    del client

    print("Loading CGO...")
    # draw CGOs
    draw_CGO(cgo_fh, model)
    print("Completed.")

    return


stored._vcontacts_id = 1
cmd.extend('Vcontacts', Vcontacts)

class CallCounter:
    """Decorator to determine number of calls for a method"""

    def __init__(self, method):
        self.method = method
        self.counter = 0

    def __call__(self, *args, **kwargs):
        self.counter += 1
        return self.method(*args, **kwargs)


class TCPClient:
    '''TCP client'''
    def __init__(self, host, port):
        try:
            self.address = (host, int(port))
        except ValueError:
            raise ValueError("Port number must be numeric.")
        self._bufferSize = 8192
        self._socket = None

    def __del__(self):
        self.close()

    def start(self):
        """Function for initializing client socket and connecting to server"""
        # create socket
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # self._socket.settimeout(15)
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
        # Send file name for server to check
        file_name = model.lower()
        fh = get_pdb_file(file_name)
        file_size = fh.tell()
        fh.close()

        # Send request CHECKFILE FILENAME FILESIZE
        request = "CHECKFILE " + file_name + " " + str(file_size)
        self._socket.sendto(request.encode(), self.address)

        # Wait for responce
        srv_resp = self._socket.recv(self._bufferSize).decode()
        # OK - Means that server already has the file
        if srv_resp == "OK":
            return True
        else:
            return False

    def send_file(self, model):
        """Sends the file to the server"""
        # Send files name
        file_name = model.lower()
        request = "SENDFILE " + file_name.lower()
        self._socket.sendto(request.encode(), self.address)

        # Wait for ACK
        srv_resp = self._socket.recv(self._bufferSize).decode()

        if srv_resp != "OK":
            raise Exception("Something went wrong...")

        fh = get_pdb_file(file_name)

        # Send files size
        file_size = fh.tell()
        fh.seek(0)

        self._socket.sendto(str(file_size).encode(), self.address)

        # Wait for ACK
        srv_resp = self._socket.recv(self._bufferSize).decode()
        if srv_resp != "OK":
            raise Exception("Something went wrong...")

        self._socket.sendall(fh.read())
        fh.close()
        srv_resp = self._socket.recv(self._bufferSize).decode()
        if srv_resp != "OK":
            raise Exception("Something went wrong...")

    def get_cgo(self, model, query):
        """get_CGO draw data"""
        file_name = model.lower()
        query_len = len(query)

        # Send GETCGO request
        request = "GETCGO " + file_name
        self._socket.sendto(request.encode(), self.address)

        # Wait for ACK
        srv_resp = self._socket.recv(self._bufferSize).decode()
        if srv_resp.split(" ")[0] != 'OK':
            raise Exception("Something went wrong...")

        # Send query len
        self._socket.sendto(str(query_len).encode(), self.address)

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
        self._socket.sendto(file_size.encode(), self.address)

        bytes_remaining = int(file_size)

        # tmp_file = tempfile.TemporaryFile()
        tmp_file = ''
        while bytes_remaining != 0:
            if bytes_remaining >= self._bufferSize:
                # receive CGOdata slab from server
                slab = self._socket.recv(self._bufferSize)
                # tmp_file.write(slab)
                tmp_file += slab.decode()
                sizeof_slab_received = len(slab)
                bytes_remaining -= int(sizeof_slab_received)
            else:
                slab = self._socket.recv(bytes_remaining)
                # tmp_file.write(slab)
                tmp_file += slab.decode()
                sizeof_slab_received = len(slab)
                bytes_remaining -= int(sizeof_slab_received)

        # tmp_file.seek(0)
        return tmp_file


def get_pdb_file(model):
    '''Returns temp file_obj handler'''
    tmp_file = tempfile.TemporaryFile()
    tmp_file.write(cmd.get_pdbstr(model).encode())
    return tmp_file


def extract_CGOs(file_object):
    '''Extracts CGOs from temp file'''
    pattern = re.compile(r'((?:COLOR|BEGIN).*?END)(.*$)')
    data = ''
    while True:
        line = file_object.readline().rstrip()
        if not line:
            break

        data += line.decode()

        for m in re.finditer(pattern, data):
            data = m.group(2)
            yield m.group(1)


def draw_CGO(fh, model):
    '''Draws CGO'''
    # CGO = list()
    # for rawCGO in extract_CGOs(fh):
    #     CGO[0:0] = [eval(cgo) for cgo in rawCGO.split(',')]
    # cmd.load_cgo(CGO, 'Vcontacts_' + model + '_' + str(stored._vcontacts_id))
    # stored._vcontacts_id += 1
    cmd.run(fh)


def get_model(model):
    """Get model if not supplied or check if given model exists in pymol"""
    all_models = cmd.get_object_list()

    if len(all_models) == 0:
        logging.error('No models are opened.')
        return

    model = model.lower()

    if model and (model in all_models):
        return model

    if len(all_models) > 1:
        logging.error("Please specify which model you want to use. {}".format(all_models))
        return

    return all_models[0]


def get_selectors_model(sele1, sele2):
    Lmodel = get_model_from_selector(sele1)
    Rmodel = get_model_from_selector(sele2)

    if (Lmodel and Rmodel) and (Lmodel != Rmodel):
        logging.error("Models in selectors does not match")
        return None

    return Lmodel


def get_model_from_selector(selector):
    if not selector:
        return None

    if not (selector in cmd.get_names('selections')):
        logging.error("No such selector: {}".format(selector))
        return None

    models = cmd.get_object_list(selector)

    if len(models) > 1:
        logging.error("Selector {} is composed from different models".format(selector))
        return None

    return models[0]


def get_serials(selector):
    if not selector:
        return ''

    atoms_ids = {'atoms': []}
    cmd.iterate(selector, 'atoms.append(ID)', space=atoms_ids)

    return ' '.join(map(str,atoms_ids['atoms']))


def Bool(arg):
    """Parse string to boolean"""
    return arg.lower() in ('y', 'true', 't', '1')


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
    seqSeparationMin,seqSeparationMax,
    # Misc.=''
    model, solvent, color, invert):
    """For composing query arguments"""

    output=""

    if Bool(color):
        output+="--random-colors "

    if not Bool(solvent):
        output+="--no-solvent "

    if Bool(invert):
        output+="--invert "

    match_first=""
    match_first=append_to_local_output(match_first, "c", get_generic_value(chainLeftIn))
    match_first=append_to_local_output(match_first, "r", get_generic_value(resiNumLeftIn))
    match_first=append_to_local_output(match_first, "a", get_generic_value(atomSerialLeftIn))
    match_first=append_to_local_output(match_first, "R", get_generic_value(resiNameLeftIn))
    match_first=append_to_local_output(match_first, "A", get_generic_value(atomNameLeftIn))
    output=append_to_global_output(output, "--match-first", match_first)

    match_first_not=""
    match_first_not=append_to_local_output(match_first_not, "c", get_generic_value(chainLeftOut))
    match_first_not=append_to_local_output(match_first_not, "r", get_generic_value(resiNumLeftOut))
    match_first_not=append_to_local_output(match_first_not, "a", get_generic_value(atomSerialLeftOut))
    match_first_not=append_to_local_output(match_first_not, "R", get_generic_value(resiNameLeftOut))
    match_first_not=append_to_local_output(match_first_not, "A", get_generic_value(atomNameLeftOut))
    output=append_to_global_output(output, "--match-first-not", match_first_not)

    match_second=""
    match_second=append_to_local_output(match_second, "c", get_generic_value(chainRightIn))
    match_second=append_to_local_output(match_second, "r", get_generic_value(resiNumRightIn))
    match_second=append_to_local_output(match_second, "a", get_generic_value(atomSerialRightIn))
    match_second=append_to_local_output(match_second, "R", get_generic_value(resiNameRightIn))
    match_second=append_to_local_output(match_second, "A", get_generic_value(atomNameRightIn))
    output=append_to_global_output(output, "--match-second", match_second)

    match_second_not=""
    match_second_not=append_to_local_output(match_second_not, "c", get_generic_value(chainRightOut))
    match_second_not=append_to_local_output(match_second_not, "r", get_generic_value(resiNumRightOut))
    match_second_not=append_to_local_output(match_second_not, "a", get_generic_value(atomSerialRightOut))
    match_second_not=append_to_local_output(match_second_not, "R", get_generic_value(resiNameRightOut))
    match_second_not=append_to_local_output(match_second_not, "A", get_generic_value(atomNameRightOut))
    output=append_to_global_output(output, "--match-second-not", match_second_not)

    output=append_to_global_output(output, "--match-min-area", get_float_value(contactAreaMin))
    output=append_to_global_output(output, "--match-max-area", get_float_value(contactAreaMax))

    output=append_to_global_output(output, "--match-min-dist", get_float_value(minimalDistanceMin))
    output=append_to_global_output(output, "--match-max-dist", get_float_value(minimalDistanceMax))

    output=append_to_global_output(output, "--match-min-seq-sep", get_int_value(seqSeparationMin))
    output=append_to_global_output(output, "--match-max-seq-sep", get_int_value(seqSeparationMax))

    return output

def get_generic_value(val):
    """Returns generic value"""
    val = [v.upper() for v in val.split()]
    return ','.join(val).replace(r"/^,+|,+$/gm",'')


def get_float_value(val):
    """Returns float value or empty string if val is not type of float"""
    try:
        a = float(val)
    except ValueError:
        return ''
    return a


def get_int_value(val):
    """Returns int value or empty string if val is not type of int"""
    try:
        a = int(val)
    except ValueError:
        return ''
    return a


def get_input_logical_value(val):
    """Returns logical value"""
    logical = '&'.join(val.split()).replace(r"/&+/gm",'&')
    logical = logical.replace(r"/&\|/gm",'|').replace(r"/\|&/gm",'|')
    logical = logical.replace(r"/\|+/gm",'|').replace(r"/^&+|&+$/gm",'')
    logical = logical.replace(r"/^\|+|\|+$/gm",'')
    return logical


def append_to_local_output(main, suffix, value):
    result=main
    if value != "":
        if result != "":
            result+="&"
        result+=suffix+"<"+str(value)+">"
    return result


def append_to_global_output(main, suffix, value):
    result=main
    if value!="":
        if result != "":
            result+=" "
        result+=suffix+" '"+str(value)+"'"
    return result
