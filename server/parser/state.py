# parser/state.py

from typing import List, Dict

from pydantic import BaseModel

# class State:
#     def __init__(self):
#         self.type: str = "state"
#         self.workflow: str = "intent_parsing"
#         self.stage: str = "ask_missing"  # ask_missing / complete
#         self.parse_success: bool = False
#         self.missing_params: List[str] = []
#         self.reason_params: List[Dict[str,str]] = []
#         self.intent_result: Dict = {}
#         self.dag: Dict = {}
#         self.code: int = 0
#         self.msg: str = ""

#     def to_dict(self) -> Dict:
#         return {
#             "type": self.type,
#             "workflow": self.workflow,
#             "stage": self.stage,
#             "parse_success": self.parse_success,
#             "missing_params": self.missing_params,
#             "reason_params": self.reason_params,
#             "intent_result": self.intent_result,
#             "dag": self.dag,
#             "code": self.code,
#             "msg": self.msg
#         }

class State(BaseModel):
    # session_id: str = ""
    session_id: str = ""
    type: str = "state"
    stage: str = "intent_parsing"
    workflow: str = "intent_parsing"
    parse_success: bool = False
    missing_params: list = []
    reason_params: list = []
    intent_result: dict = {}
    dag: dict = {}
    code:int =0
    msg:str = ""