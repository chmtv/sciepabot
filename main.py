import subprocess
import json
from math import floor
from cannabis import get_strain_info_str, search_strain_names_list

signalpath = "../signal-cli"
phoneNo = "+48739030228"
p = subprocess.Popen('../signal-cli jsonRpc'.split(), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

def sendMessage(receiver, message):
    subprocess.call(f'{signalpath} -a send -m {message} {receiver}', shell=True)
def sendMessageToGroup(group_id, message):
    json_req = '{"jsonrpc":"2.0","method":"send","params":{"groupId":["'+group_id+'"],"message":"'+message+'"},"id":6}\n'
    json_req = json_req.encode()
    p.stdin.write(json_req)
    p.stdin.flush()
    print(f'Sent message to group {group_id} \n Message content:\n {message}')

# To be used later maybe
class Command:
    def __init__(self, command:str, args_n):
        self.command = command
        self.args_n = args_n
class Skladka:
    total : float
    userAmounts = {}
    def __init__(self):
        self.total = 0
        self.userAmounts = []
skladkas = {}
def totalCurrencyStr(amount):
    # bn - banknote
    # c - coin
    # v - 200
    # papaj - 2137
    
    papaj_value = 2137
    v_value = 200
    bn_value = 50

    papaj_symbol = "(👴🍰)"
    v_symbol = "💰"
    old_v_symbol = "♈"

    print("no kruwa funckaj z tego total stringa")
    print(type(amount))
    print(type(papaj_value))


    papaj_amount = floor(amount / papaj_value)
    papaj_in_pln = papaj_amount * papaj_value
    papaj_count_str = papaj_symbol * papaj_amount

    v_amount = floor( (amount-papaj_in_pln) / v_value)
    v_in_pln = v_amount * v_value
    v_count_str = v_symbol * v_amount

    bn_amount = floor( (amount-papaj_in_pln-v_in_pln) / bn_value)
    bn_in_pln = bn_amount * bn_value
    bn_count_str = "💵" * bn_amount
    
    c_amount = floor( (amount-papaj_in_pln-v_in_pln-bn_in_pln) / 5) % 50
    c_count_str = "🪙" * c_amount

    # return {
    #     "v": v_count_str,
    #     "bn": bn_count_str,
    #     "c": c_count_str
    # }
    return f'{papaj_count_str}{v_count_str}{bn_count_str}{c_count_str}'
def groupskladkaStatusMsg(group_id):
    skladka = skladkas[group_id]["currencies"]
    sciepa_name = ""
    print("SCIEPA NAME ")
    try:
        print(skladka["data"]["name"])
        sciepa_name = skladka["data"]["name"] if skladka["data"]["name"] else ""
    except KeyError:
        pass
    msg = f'Status składki {sciepa_name}:\\n'
    total = 0
    for username, amount in skladka.items():
        currency_str = totalCurrencyStr(amount)

        total += amount
        msg += f'{username}: {amount}zł - {currency_str} \\n'
    total_str = totalCurrencyStr(total)
    msg += f'Całość: {total}zł {total_str}'
    return msg

# also for later
def validateCommandMsg(text : str, command : str):
    if text and \
    text.startswith(command):
        return true
def processGroupMsg(msg):
    sourceNumber : str= "+48123456789"
    envelope = {}
    msg_text : str = ""
    if "params" in msg:
        envelope = msg["params"]["envelope"]
        sourceNumber = envelope["sourceNumber"]
    else:
        print("Params not found, aborting")
        return
    msg_text = envelope["dataMessage"]["message"] if ("dataMessage" in envelope) else ""
    if not msg_text:
        print("No msg_text")
        return
    msg_text = msg_text.lower()
    group_id : str = envelope["dataMessage"]["groupInfo"]["groupId"]
    source_name = envelope["sourceName"]
    msg_split = msg_text.split()
    print("~~~Processing group message~~~")
    print("msg_text:   ", msg_text)
    print("msg dict: ", msg)
    #
    # Command
    # /skladka /status
    # Wysyla status skladki
    #CHUJOWE ROZWIĄZANIE : VVV
    if msg_text == "/skladka" or msg_text == "/status":
        res_str = groupskladkaStatusMsg(group_id)
        sendMessageToGroup(group_id, res_str)
    #
    # Command
    # /dodaj [amount:float]
    # Dodaje amount złotych do użytkownika w ściepie w grupie wiadomości komendy  
    # 
    
    if msg_text.startswith("/dodaj"):
        res_msg = ""
        print("msg", msg)
        envelope = msg["params"]["envelope"] # A double variable, inefficient, but im lazy rn
        amount = 0
        if msg_text and not len(msg_split) < 3 and msg_split[1].isnumeric():
            res_msg = "Błąd, upewnij się że podałeś liczbę jako argument!"
            sendMessageToGroup(group_id, res_msg)
            return
        if len(msg_split) < 2:
            sendMessageToGroup(group_id, "Błąd, zła liczba argumentów")
            return
        # Update the sciepa data
        amount = float(msg_split[1])
        
        if group_id not in skladkas:
            # Init the sciepa
            skladkas[group_id] = {}
            skladkas[group_id]["currencies"] = {}
            skladkas[group_id]["data"] = {}
            skladkas[group_id]["currencies"][source_name] = amount
        else:
            if source_name in skladkas[group_id]["currencies"]:
                skladkas[group_id]["currencies"][source_name] += amount
            else:
                skladkas[group_id]["currencies"][source_name] = amount
        sendMessageToGroup(group_id, groupskladkaStatusMsg(group_id))
    #
    # Command
    # /skladka
    # Resetuje skladke i opcjonalnie ustawia nazwe
    # 
    if msg_text.startswith("/reset"):
        res_msg = "Zresetowano ściepę "

        # Set the name for sciepa if specified
        msg_split = msg_text.split()
        sciepa_name = ""
        if len(msg_split) > 1:
            sciepa_name = msg_split[1]
        res_msg += sciepa_name
        skladkas[group_id]["data"]["name"] = sciepa_name
        
        # Reset sciepa
        
        group_id = envelope["dataMessage"]["groupInfo"]["groupId"]
        
        if group_id in skladkas:
            skladkas[group_id]["data"] = {"name": ""}
            skladkas[group_id]["currencies"] = {}
            sendMessageToGroup(group_id, res_msg)
        else:
            sendMessageToGroup(group_id, "Błąd, nie ma ściepy")
        
    #
    # Command
    # /help
    # help, imo kiedyś go dodam
    # 
    if msg_text == "/help":
        help_str = " ".join([
            " \\n",
            "ℹ️ Manual ChemolTV Bot ℹ️ \\n",
            "/help - Pokazuje pomoc (no przecież) \\n",
                    "\\n",
                "💰 Składka 💰 \\n",
            "/dodaj [ilość] - dodaje podaną ilość PLNów do składki, wyświetla następnie status składki \\n",
            "/skladka, /status - pokazuje status składki \\n",
            "/reset - resetuje składkę do stanu początkowego \\n",
                    "\\n",
                "🌿 Przeglądarka odmian Strain Browser :DD 🌿 \\n",
            "/strain [nazwa] - pokazuje informacje o odmianie o podanej nazwie (aktualnie trzeba wpisywać z wielkimi literami) \\n",
            "/szukaj [nazwa] - podaje listę odmian zawierających w sobie podane hasło \\n"
        ])
        sendMessageToGroup(group_id, help_str)


    #
    # Command
    # /strain
    # Pokazuje info z cannabis.csv o strainie o podanej nazwie
    # 
    if msg_text.startswith("/strain"):
        print(msg_split)
        if len(msg_split) < 2:
            sendMessageToGroup(group_id, "Błąd, zła liczba argumentów")
            return
        strain_str = get_strain_info_str(msg_split[1])
        sendMessageToGroup(group_id, strain_str)
    if msg_text.startswith("/szukaj"):
        print(msg_split)
        if len(msg_split) < 2:
            sendMessageToGroup(group_id, "Błąd, zła liczba argumentów")
            return
        strain_list = search_strain_names_list(msg_split[1])
        list_str = "Znalezione odmiany: \\n"
        for name in strain_list:
            list_str += f' - {name}\\n'
        sendMessageToGroup(group_id, list_str)

def processBotMsg(msg):
    # Additional checks to be made:
    ## AttributeError: 'NoneType' object has no attribute 'startswith'

    # Mainly boilerplate:
    # This will need a rework i'm not thinking properly and am tired right now
    try:
        # Check whether group data is in the msg dict
        print("Processing message:")
        print(msg)
        envelope = msg["params"]["envelope"]
        if "dataMessage" in envelope and "groupInfo" in envelope["dataMessage"]:
            processGroupMsg(msg)
        else: # Currently no Direct Message commands
            # user = 
            # sendMessage()
            return
    except KeyError as err:
        print("KeyError wyjebało ;(((((")
        print(err)
# Code for reading the received messages
def runProcess(exe):    
    # print("chemoltv counter 419 ready")
    while(True):
        # returns None while subprocess is running
        # retcode = p.poll() 
        line = p.stdout.readline()
        yield line
        #if retcode is not None:
        #    break
for line in runProcess('../signal-cli jsonRpc'.split()):
    proper_line = line.decode("utf-8")
    msg = {}
    if proper_line[0] == "{": 
        msg = json.loads(proper_line)
        processBotMsg(msg)



