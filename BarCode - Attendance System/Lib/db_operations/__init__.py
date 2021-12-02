from datetime import datetime


def decide_check_type(l_checkin: str, l_checkout: str):
    """
    compares last check in and check-out times and decides whether to check-in or check-out at present time
    :param l_checkin:
    :param l_checkout:
    :return:
    """
    if l_checkout and l_checkin:  # none of them are blanks or none
        checkin_obj = datetime.strptime(l_checkin, "%H:%M")
        checkout_obj = datetime.strptime(l_checkout, "%H:%M")

        if checkin_obj > checkout_obj:
            return "checked in"
        else:
            return "checked out"
    else:
        if not l_checkout:
            return "checked in"
        elif not l_checkin:
            return "checked out"
