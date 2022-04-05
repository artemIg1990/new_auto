
import re
from datetime import datetime


class Case:

    def __init__(self, predicate, name, test_rail_id) -> None:
        self.test_rail_id = test_rail_id
        self.name = name
        self.predicate = predicate

    def test(self, messages, update_message_idx):
        return self.predicate(messages, update_message_idx)


def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")


# https://omnicqa.testrail.io/index.php?/cases/view/967
# Upload completed successfully
# Has at least one update log
def case1(messages, update_message_idx):
    result = update_message_idx is not None
    if result:
        return True
    else:
        return False


# https://omnicqa.testrail.io/index.php?/cases/view/968
# Connected to Vendotek
# Has at least one "Connected to Vendotek" log
def case2(messages, update_message_idx):
    if update_message_idx is None:
        return False
    after_update_message = messages[update_message_idx + 1:]
    log_entry = "Connected to Vendotek"
    result = any(log_entry in elem["message"]["message"] for elem in after_update_message)
    return result


# https://omnicqa.testrail.io/index.php?/cases/view/969
# MQTT: Connected! DIS_ERR: 0 | UN_ERR: 0
# Has at least one "MQTT: Connected! DIS_ERR: 0 | UN_ERR: 0" log
def case3(messages, update_message_idx):
    if update_message_idx is None:
        return False
    after_update_message = messages[update_message_idx + 1:]
    log_entry = "MQTT: Connected! DIS_ERR: 0 | UN_ERR: 0"
    result = any(log_entry in elem["message"]["message"] for elem in after_update_message)
    return result


# https://omnicqa.testrail.io/index.php?/cases/view/970
# Message: Memory entries read, not less count 100
# Has all values greater than 100 in the first "Memory entries read" log
def case4(messages, update_message_idx):
    if update_message_idx is None:
        return False
    after_update_message = messages[update_message_idx + 1:]
    log_entry = "Memory entries read SUCCESS!"

    result_message = next((x for x in after_update_message if log_entry in x["message"]["message"]), None)
    if result_message is None:
        return False

    message_text = result_message["message"]["message"]
    digits = [int(s) for s in message_text.split() if s.isdigit()]
    result = all(elem > 100 for elem in digits)
    return result


# https://omnicqa.testrail.io/index.php?/cases/view/971
# Count placed orders BD Controller vs Server
# Manual case
def case5(messages, update_message_idx):
    # Manual case
    return None


# https://omnicqa.testrail.io/index.php?/cases/view/972
# Message: Start Global update link check!
# Has at least <hours_passed - 1> "Global update link check" logs
def case6(messages, update_message_idx):
    if update_message_idx is None:
        return False
    after_update_message = messages[update_message_idx + 1:]

    first_after_update_message = after_update_message[0]
    last_after_update_message = after_update_message[-1]

    hours_between_messages = (parse_date(last_after_update_message["message"]["timestamp"]) -
                              parse_date(first_after_update_message["message"]["timestamp"])
                              ).total_seconds() / 3600

    log_entry = "Global update link check"
    result = sum(log_entry in elem["message"]["message"] for elem in after_update_message)
    return result >= hours_between_messages - 1


# https://omnicqa.testrail.io/index.php?/cases/view/973
# Not abnormal message:MEMORY: Heap free, too low
# Has less or equal than one "TOO LOW" log
def case7(messages, update_message_idx):
    if update_message_idx is None:
        return False
    after_update_message = messages[update_message_idx + 1:]
    log_entry = "TOO LOW!"
    result = sum(log_entry in elem["message"]["message"] for elem in after_update_message)
    return result <= 1


# https://omnicqa.testrail.io/index.php?/cases/view/974
# Order sync. Sent to rmq!
# Has at least one " sync. Sent to rmq!" log
def case8(messages, update_message_idx):
    if update_message_idx is None:
        return False
    after_update_message = messages[update_message_idx + 1:]
    log_entry = " sync. Sent to rmq!"
    result = any(log_entry in elem["message"]["message"] for elem in after_update_message)
    return result


# https://omnicqa.testrail.io/index.php?/cases/view/975
# Send payment result
# Has at least one "Payment result: Session" log
def case9(messages, update_message_idx):
    if update_message_idx is None:
        return False
    after_update_message = messages[update_message_idx + 1:]
    log_entry = "Payment result: Session"
    result = any(log_entry in elem["message"]["message"] for elem in after_update_message)
    return result


# https://omnicqa.testrail.io/index.php?/cases/view/976
# Correctly processes the command "boxOperationRequest | cell/open"
# Has at least one "Cell <num> opened" or "Cell <num> closed" log
def case10(messages, update_message_idx):
    if update_message_idx is None:
        return False
    after_update_message = messages[update_message_idx + 1:]
    # log_entry = "Upload FAILED!"
    regex = re.compile(r'^Cell \d+ ((\bopened\b)|(\bclosed\b))')
    result = any(regex.match(elem["message"]["message"]) for elem in after_update_message)
    return result


# https://omnicqa.testrail.io/index.php?/cases/view/977
# Correctly processes send status cell
# Has at least one "PUSH_STATUS_CELL" log
def case11(messages, update_message_idx):
    if update_message_idx is None:
        return False
    after_update_message = messages[update_message_idx + 1:]
    log_entry = "PUSH_STATUS_CELL"
    result = any(log_entry in elem["message"]["message"] for elem in after_update_message)
    return result


# https://omnicqa.testrail.io/index.php?/cases/view/979
# Not abnormal message: Upload FAILED! STAGE
# Has no "Upload FAILED!" logs
def case12(messages, update_message_idx):
    if update_message_idx is None:
        return False
    after_update_message = messages[update_message_idx + 1:]
    log_entry = "Upload FAILED!"
    result = any(log_entry in elem["message"]["message"] for elem in after_update_message)
    return not result


# https://omnicqa.testrail.io/index.php?/cases/view/983
# Not abnormal message: "RST: SW"
# Has exactly one "RST: SW" log
def case13(messages, update_message_idx):
    if update_message_idx is None:
        return False
    after_update_message = messages[update_message_idx + 1:]
    log_entry = "RST: SW"
    result = sum(log_entry in elem["message"]["message"] for elem in after_update_message)
    return result == 1


# https://omnicqa.testrail.io/index.php?/cases/view/984
# Not abnormal message: Cant conected Vendotek
# Has less or equal than one "Cant conected Vendotek" log
def case14(messages, update_message_idx):
    if update_message_idx is None:
        return False
    after_update_message = messages[update_message_idx + 1:]
    log_entry = "Cant connect to Vendotek"
    result = sum(log_entry in elem["message"]["message"] for elem in after_update_message)
    return result <= 1


# https://omnicqa.testrail.io/index.php?/cases/view/980
# Not message: MEMORY: 52000 during 10 min! RESTART
# Has no "MEMORY: 52000" logs
def case15(messages, update_message_idx):
    if update_message_idx is None:
        return False
    after_update_message = messages[update_message_idx + 1:]
    log_entry = "MEMORY: 52000"
    result = any(log_entry in elem["message"]["message"] for elem in after_update_message)
    return not result


# https://omnicqa.testrail.io/index.php?/cases/view/981
# Not message MQTT: Connected! with counted DIS_ERR: and UN_ERR
# Has all "DIS_ERR: " and "UN_ERR: " values equal to 0
def case16(messages, update_message_idx):
    if update_message_idx is None:
        return False
    after_update_message = messages[update_message_idx + 1:]
    log_entry = "MQTT: Connected!"

    result_message = next((x for x in after_update_message if log_entry in x["message"]["message"]), None)
    if result_message is None:
        return False

    message_text = result_message["message"]["message"]
    digits = [int(s) for s in message_text.split() if s.isdigit()]
    result = all(elem == 0 for elem in digits)
    return result


# https://omnicqa.testrail.io/index.php?/cases/view/982
# Not message: "RST: PANIC"
# Has no "RST: PANIC" logs
def case17(messages, update_message_idx):
    if update_message_idx is None:
        return False
    after_update_message = messages[update_message_idx + 1:]
    log_entry = "RST: PANIC"
    result = any(log_entry in elem["message"]["message"] for elem in after_update_message)
    return not result


cases = [
    Case(case1, "Upload completed successfully", 967),
    Case(case2, "Connected to Vendotek", 968),
    Case(case3, "MQTT: Connected! DIS_ERR: 0 | UN_ERR: 0", 969),
    Case(case4, "Message: Memory entries read, not less count 100", 970),
    Case(case5, "Count placed orders BD Controller vs Server", 971),
    Case(case6, "Message: Start Global update link check!", 972),
    Case(case7, "Not abnormal message:MEMORY: Heap free, too low", 973),
    Case(case8, "Order sync. Sent to rmq!", 974),
    Case(case9, "Send payment result", 975),
    Case(case10, "Correctly processes the command \"boxOperationRequest | cell/open\"", 976),
    Case(case11, "Correctly processes send status cell", 977),
    Case(case12, "Not abnormal message: Upload FAILED! STAGE", 979),
    Case(case13, "Not abnormal message: RST: SW", 983),
    Case(case14, "Not abnormal message: Cant conected Vendotek", 984),
    Case(case15, "Not message: MEMORY: 52000 during 10 min! RESTART", 980),
    Case(case16, "Not message: MQTT: Connected! with counted DIS_ERR: and UN_ERR", 981),
    Case(case17, "Not message: RST: PANIC", 982)
]
