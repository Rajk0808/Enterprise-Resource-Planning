import sys
def get_error_info(error, error_detail: sys): # type: ignore
        _, _, exc_tb = error_detail.exc_info()
        filename = exc_tb.tb_frame.f_code.co_filename # type: ignore
        error_massage = 'Error occured in python script file {0}, Line number [{1}], Error Massage [{2}]'.format(
                filename,
                exc_tb.tb_lineno, # type: ignore
                str(error)
        )
        return error_massage

class CustomException(Exception):
    def __init__(self, error_massage, error_detail:sys): # type: ignore
        super().__init__(error_massage)
        self.error_massage = get_error_info(error_massage, error_detail)
    
    def __str__(self):
        return self.error_massage
