import allure


def print_log(log_name, log_message):
    allure.attach(log_message, name=log_name, attachment_type=allure.attachment_type.TEXT)
    print(log_name)
    print(log_message)