import base64
import dataclasses
import typing
from abc import ABC, abstractmethod

import algokit_utils
import algosdk
from algosdk.v2client import models
from algosdk.atomic_transaction_composer import (
    TransactionSigner
)

_APP_SPEC_JSON = r"""{
    "hints": {
        "quiz_data(string,string,string,string,string)void": {
            "call_config": {
                "no_op": "CALL"
            }
        }
    },
    "source": {
        "approval": "I3ByYWdtYSB2ZXJzaW9uIDEwCgpzbWFydF9jb250cmFjdHMuaGVsbG9fd29ybGQuY29udHJhY3QuSGVsbG9Xb3JsZC5hcHByb3ZhbF9wcm9ncmFtOgogICAgLy8gc21hcnRfY29udHJhY3RzL2hlbGxvX3dvcmxkL2NvbnRyYWN0LnB5OjUKICAgIC8vIGNsYXNzIEhlbGxvV29ybGQoQVJDNENvbnRyYWN0KToKICAgIHR4biBOdW1BcHBBcmdzCiAgICBieiBtYWluX2JhcmVfcm91dGluZ0A1CiAgICBtZXRob2QgInF1aXpfZGF0YShzdHJpbmcsc3RyaW5nLHN0cmluZyxzdHJpbmcsc3RyaW5nKXZvaWQiCiAgICB0eG5hIEFwcGxpY2F0aW9uQXJncyAwCiAgICBtYXRjaCBtYWluX3F1aXpfZGF0YV9yb3V0ZUAyCiAgICBlcnIgLy8gcmVqZWN0IHRyYW5zYWN0aW9uCgptYWluX3F1aXpfZGF0YV9yb3V0ZUAyOgogICAgLy8gc21hcnRfY29udHJhY3RzL2hlbGxvX3dvcmxkL2NvbnRyYWN0LnB5OjcKICAgIC8vIEBhYmltZXRob2QoKQogICAgdHhuIE9uQ29tcGxldGlvbgogICAgIQogICAgYXNzZXJ0IC8vIE9uQ29tcGxldGlvbiBpcyBOb09wCiAgICB0eG4gQXBwbGljYXRpb25JRAogICAgYXNzZXJ0IC8vIGlzIG5vdCBjcmVhdGluZwogICAgLy8gc21hcnRfY29udHJhY3RzL2hlbGxvX3dvcmxkL2NvbnRyYWN0LnB5OjUKICAgIC8vIGNsYXNzIEhlbGxvV29ybGQoQVJDNENvbnRyYWN0KToKICAgIHR4bmEgQXBwbGljYXRpb25BcmdzIDEKICAgIGV4dHJhY3QgMiAwCiAgICB0eG5hIEFwcGxpY2F0aW9uQXJncyAyCiAgICBleHRyYWN0IDIgMAogICAgdHhuYSBBcHBsaWNhdGlvbkFyZ3MgMwogICAgZXh0cmFjdCAyIDAKICAgIHR4bmEgQXBwbGljYXRpb25BcmdzIDQKICAgIGV4dHJhY3QgMiAwCiAgICB0eG5hIEFwcGxpY2F0aW9uQXJncyA1CiAgICBleHRyYWN0IDIgMAogICAgLy8gc21hcnRfY29udHJhY3RzL2hlbGxvX3dvcmxkL2NvbnRyYWN0LnB5OjcKICAgIC8vIEBhYmltZXRob2QoKQogICAgY2FsbHN1YiBxdWl6X2RhdGEKICAgIGludCAxCiAgICByZXR1cm4KCm1haW5fYmFyZV9yb3V0aW5nQDU6CiAgICAvLyBzbWFydF9jb250cmFjdHMvaGVsbG9fd29ybGQvY29udHJhY3QucHk6NQogICAgLy8gY2xhc3MgSGVsbG9Xb3JsZChBUkM0Q29udHJhY3QpOgogICAgdHhuIE9uQ29tcGxldGlvbgogICAgIQogICAgYXNzZXJ0IC8vIHJlamVjdCB0cmFuc2FjdGlvbgogICAgdHhuIEFwcGxpY2F0aW9uSUQKICAgICEKICAgIGFzc2VydCAvLyBpcyBjcmVhdGluZwogICAgaW50IDEKICAgIHJldHVybgoKCi8vIHNtYXJ0X2NvbnRyYWN0cy5oZWxsb193b3JsZC5jb250cmFjdC5IZWxsb1dvcmxkLnF1aXpfZGF0YSh3YWxsZXRfYWRkcmVzczogYnl0ZXMsIGJvb2tsZXQ6IGJ5dGVzLCBzdGFydF90aW1lOiBieXRlcywgcXVlX2FuczogYnl0ZXMsIGVuZF90aW1lOiBieXRlcykgLT4gdm9pZDoKcXVpel9kYXRhOgogICAgLy8gc21hcnRfY29udHJhY3RzL2hlbGxvX3dvcmxkL2NvbnRyYWN0LnB5OjctMTUKICAgIC8vIEBhYmltZXRob2QoKQogICAgLy8gZGVmIHF1aXpfZGF0YSgKICAgIC8vICAgICBzZWxmLAogICAgLy8gICAgIHdhbGxldF9hZGRyZXNzOiBTdHJpbmcsCiAgICAvLyAgICAgYm9va2xldDogU3RyaW5nLAogICAgLy8gICAgIHN0YXJ0X3RpbWU6IFN0cmluZywKICAgIC8vICAgICBxdWVfYW5zOiBTdHJpbmcsCiAgICAvLyAgICAgZW5kX3RpbWU6IFN0cmluZywKICAgIC8vICkgLT4gTm9uZToKICAgIHByb3RvIDUgMAogICAgLy8gc21hcnRfY29udHJhY3RzL2hlbGxvX3dvcmxkL2NvbnRyYWN0LnB5OjE2CiAgICAvLyBzZWxmLnJlc2V0X2dsb2JhbF9zdGF0ZSgpCiAgICBjYWxsc3ViIHJlc2V0X2dsb2JhbF9zdGF0ZQogICAgLy8gc21hcnRfY29udHJhY3RzL2hlbGxvX3dvcmxkL2NvbnRyYWN0LnB5OjE3CiAgICAvLyBzZWxmLmdsb2JhbF93YWxsZXRfYWRkcmVzcyA9IHdhbGxldF9hZGRyZXNzCiAgICBieXRlICJnbG9iYWxfd2FsbGV0X2FkZHJlc3MiCiAgICBmcmFtZV9kaWcgLTUKICAgIGFwcF9nbG9iYWxfcHV0CiAgICAvLyBzbWFydF9jb250cmFjdHMvaGVsbG9fd29ybGQvY29udHJhY3QucHk6MTgKICAgIC8vIHNlbGYuZ2xvYmFsX2Jvb2tsZXQgPSBib29rbGV0CiAgICBieXRlICJnbG9iYWxfYm9va2xldCIKICAgIGZyYW1lX2RpZyAtNAogICAgYXBwX2dsb2JhbF9wdXQKICAgIC8vIHNtYXJ0X2NvbnRyYWN0cy9oZWxsb193b3JsZC9jb250cmFjdC5weToxOQogICAgLy8gc2VsZi5nbG9iYWxfc3RhcnRfdGltZSA9IHN0YXJ0X3RpbWUKICAgIGJ5dGUgImdsb2JhbF9zdGFydF90aW1lIgogICAgZnJhbWVfZGlnIC0zCiAgICBhcHBfZ2xvYmFsX3B1dAogICAgLy8gc21hcnRfY29udHJhY3RzL2hlbGxvX3dvcmxkL2NvbnRyYWN0LnB5OjIwCiAgICAvLyBzZWxmLmdsb2JhbF9xdWVfYW5zID0gcXVlX2FucwogICAgYnl0ZSAiZ2xvYmFsX3F1ZV9hbnMiCiAgICBmcmFtZV9kaWcgLTIKICAgIGFwcF9nbG9iYWxfcHV0CiAgICAvLyBzbWFydF9jb250cmFjdHMvaGVsbG9fd29ybGQvY29udHJhY3QucHk6MjEKICAgIC8vIHNlbGYuZ2xvYmFsX2VuZF90aW1lID0gZW5kX3RpbWUKICAgIGJ5dGUgImdsb2JhbF9lbmRfdGltZSIKICAgIGZyYW1lX2RpZyAtMQogICAgYXBwX2dsb2JhbF9wdXQKICAgIHJldHN1YgoKCi8vIHNtYXJ0X2NvbnRyYWN0cy5oZWxsb193b3JsZC5jb250cmFjdC5IZWxsb1dvcmxkLnJlc2V0X2dsb2JhbF9zdGF0ZSgpIC0+IHZvaWQ6CnJlc2V0X2dsb2JhbF9zdGF0ZToKICAgIC8vIHNtYXJ0X2NvbnRyYWN0cy9oZWxsb193b3JsZC9jb250cmFjdC5weToyMy0yNAogICAgLy8gQHN1YnJvdXRpbmUKICAgIC8vIGRlZiByZXNldF9nbG9iYWxfc3RhdGUoc2VsZikgLT4gTm9uZToKICAgIHByb3RvIDAgMAogICAgLy8gc21hcnRfY29udHJhY3RzL2hlbGxvX3dvcmxkL2NvbnRyYWN0LnB5OjE3CiAgICAvLyBzZWxmLmdsb2JhbF93YWxsZXRfYWRkcmVzcyA9IHdhbGxldF9hZGRyZXNzCiAgICBieXRlICJnbG9iYWxfd2FsbGV0X2FkZHJlc3MiCiAgICAvLyBzbWFydF9jb250cmFjdHMvaGVsbG9fd29ybGQvY29udHJhY3QucHk6MjUKICAgIC8vIHNlbGYuZ2xvYmFsX3dhbGxldF9hZGRyZXNzID0gU3RyaW5nKCIiKQogICAgYnl0ZSAiIgogICAgYXBwX2dsb2JhbF9wdXQKICAgIC8vIHNtYXJ0X2NvbnRyYWN0cy9oZWxsb193b3JsZC9jb250cmFjdC5weToxOAogICAgLy8gc2VsZi5nbG9iYWxfYm9va2xldCA9IGJvb2tsZXQKICAgIGJ5dGUgImdsb2JhbF9ib29rbGV0IgogICAgLy8gc21hcnRfY29udHJhY3RzL2hlbGxvX3dvcmxkL2NvbnRyYWN0LnB5OjI2CiAgICAvLyBzZWxmLmdsb2JhbF9ib29rbGV0ID0gU3RyaW5nKCIiKQogICAgYnl0ZSAiIgogICAgYXBwX2dsb2JhbF9wdXQKICAgIC8vIHNtYXJ0X2NvbnRyYWN0cy9oZWxsb193b3JsZC9jb250cmFjdC5weToxOQogICAgLy8gc2VsZi5nbG9iYWxfc3RhcnRfdGltZSA9IHN0YXJ0X3RpbWUKICAgIGJ5dGUgImdsb2JhbF9zdGFydF90aW1lIgogICAgLy8gc21hcnRfY29udHJhY3RzL2hlbGxvX3dvcmxkL2NvbnRyYWN0LnB5OjI3CiAgICAvLyBzZWxmLmdsb2JhbF9zdGFydF90aW1lID0gU3RyaW5nKCIiKQogICAgYnl0ZSAiIgogICAgYXBwX2dsb2JhbF9wdXQKICAgIC8vIHNtYXJ0X2NvbnRyYWN0cy9oZWxsb193b3JsZC9jb250cmFjdC5weToyMAogICAgLy8gc2VsZi5nbG9iYWxfcXVlX2FucyA9IHF1ZV9hbnMKICAgIGJ5dGUgImdsb2JhbF9xdWVfYW5zIgogICAgLy8gc21hcnRfY29udHJhY3RzL2hlbGxvX3dvcmxkL2NvbnRyYWN0LnB5OjI4CiAgICAvLyBzZWxmLmdsb2JhbF9xdWVfYW5zID0gU3RyaW5nKCIiKQogICAgYnl0ZSAiIgogICAgYXBwX2dsb2JhbF9wdXQKICAgIC8vIHNtYXJ0X2NvbnRyYWN0cy9oZWxsb193b3JsZC9jb250cmFjdC5weToyMQogICAgLy8gc2VsZi5nbG9iYWxfZW5kX3RpbWUgPSBlbmRfdGltZQogICAgYnl0ZSAiZ2xvYmFsX2VuZF90aW1lIgogICAgLy8gc21hcnRfY29udHJhY3RzL2hlbGxvX3dvcmxkL2NvbnRyYWN0LnB5OjI5CiAgICAvLyBzZWxmLmdsb2JhbF9lbmRfdGltZSA9IFN0cmluZygiIikKICAgIGJ5dGUgIiIKICAgIGFwcF9nbG9iYWxfcHV0CiAgICByZXRzdWIK",
        "clear": "I3ByYWdtYSB2ZXJzaW9uIDEwCgpzbWFydF9jb250cmFjdHMuaGVsbG9fd29ybGQuY29udHJhY3QuSGVsbG9Xb3JsZC5jbGVhcl9zdGF0ZV9wcm9ncmFtOgogICAgLy8gc21hcnRfY29udHJhY3RzL2hlbGxvX3dvcmxkL2NvbnRyYWN0LnB5OjUKICAgIC8vIGNsYXNzIEhlbGxvV29ybGQoQVJDNENvbnRyYWN0KToKICAgIGludCAxCiAgICByZXR1cm4K"
    },
    "state": {
        "global": {
            "num_byte_slices": 5,
            "num_uints": 0
        },
        "local": {
            "num_byte_slices": 0,
            "num_uints": 0
        }
    },
    "schema": {
        "global": {
            "declared": {
                "global_booklet": {
                    "type": "bytes",
                    "key": "global_booklet"
                },
                "global_end_time": {
                    "type": "bytes",
                    "key": "global_end_time"
                },
                "global_que_ans": {
                    "type": "bytes",
                    "key": "global_que_ans"
                },
                "global_start_time": {
                    "type": "bytes",
                    "key": "global_start_time"
                },
                "global_wallet_address": {
                    "type": "bytes",
                    "key": "global_wallet_address"
                }
            },
            "reserved": {}
        },
        "local": {
            "declared": {},
            "reserved": {}
        }
    },
    "contract": {
        "name": "HelloWorld",
        "methods": [
            {
                "name": "quiz_data",
                "args": [
                    {
                        "type": "string",
                        "name": "wallet_address"
                    },
                    {
                        "type": "string",
                        "name": "booklet"
                    },
                    {
                        "type": "string",
                        "name": "start_time"
                    },
                    {
                        "type": "string",
                        "name": "que_ans"
                    },
                    {
                        "type": "string",
                        "name": "end_time"
                    }
                ],
                "returns": {
                    "type": "void"
                }
            }
        ],
        "networks": {}
    },
    "bare_call_config": {
        "no_op": "CREATE"
    }
}"""
APP_SPEC = algokit_utils.ApplicationSpecification.from_json(_APP_SPEC_JSON)
_TReturn = typing.TypeVar("_TReturn")


class _ArgsBase(ABC, typing.Generic[_TReturn]):
    @staticmethod
    @abstractmethod
    def method() -> str:
        ...


_TArgs = typing.TypeVar("_TArgs", bound=_ArgsBase[typing.Any])


@dataclasses.dataclass(kw_only=True)
class _TArgsHolder(typing.Generic[_TArgs]):
    args: _TArgs


def _filter_none(value: dict | typing.Any) -> dict | typing.Any:
    if isinstance(value, dict):
        return {k: _filter_none(v) for k, v in value.items() if v is not None}
    return value


def _as_dict(data: typing.Any, *, convert_all: bool = True) -> dict[str, typing.Any]:
    if data is None:
        return {}
    if not dataclasses.is_dataclass(data):
        raise TypeError(f"{data} must be a dataclass")
    if convert_all:
        result = dataclasses.asdict(data)
    else:
        result = {f.name: getattr(data, f.name) for f in dataclasses.fields(data)}
    return _filter_none(result)


def _convert_transaction_parameters(
    transaction_parameters: algokit_utils.TransactionParameters | None,
) -> algokit_utils.TransactionParametersDict:
    return typing.cast(algokit_utils.TransactionParametersDict, _as_dict(transaction_parameters))


def _convert_call_transaction_parameters(
    transaction_parameters: algokit_utils.TransactionParameters | None,
) -> algokit_utils.OnCompleteCallParametersDict:
    return typing.cast(algokit_utils.OnCompleteCallParametersDict, _as_dict(transaction_parameters))


def _convert_create_transaction_parameters(
    transaction_parameters: algokit_utils.TransactionParameters | None,
    on_complete: algokit_utils.OnCompleteActionName,
) -> algokit_utils.CreateCallParametersDict:
    result = typing.cast(algokit_utils.CreateCallParametersDict, _as_dict(transaction_parameters))
    on_complete_enum = on_complete.replace("_", " ").title().replace(" ", "") + "OC"
    result["on_complete"] = getattr(algosdk.transaction.OnComplete, on_complete_enum)
    return result


def _convert_deploy_args(
    deploy_args: algokit_utils.DeployCallArgs | None,
) -> algokit_utils.ABICreateCallArgsDict | None:
    if deploy_args is None:
        return None

    deploy_args_dict = typing.cast(algokit_utils.ABICreateCallArgsDict, _as_dict(deploy_args))
    if isinstance(deploy_args, _TArgsHolder):
        deploy_args_dict["args"] = _as_dict(deploy_args.args)
        deploy_args_dict["method"] = deploy_args.args.method()

    return deploy_args_dict


@dataclasses.dataclass(kw_only=True)
class QuizDataArgs(_ArgsBase[None]):
    wallet_address: str
    booklet: str
    start_time: str
    que_ans: str
    end_time: str

    @staticmethod
    def method() -> str:
        return "quiz_data(string,string,string,string,string)void"


class ByteReader:
    def __init__(self, data: bytes):
        self._data = data

    @property
    def as_bytes(self) -> bytes:
        return self._data

    @property
    def as_str(self) -> str:
        return self._data.decode("utf8")

    @property
    def as_base64(self) -> str:
        return base64.b64encode(self._data).decode("utf8")

    @property
    def as_hex(self) -> str:
        return self._data.hex()


class GlobalState:
    def __init__(self, data: dict[bytes, bytes | int]):
        self.global_booklet = ByteReader(typing.cast(bytes, data.get(b"global_booklet")))
        self.global_end_time = ByteReader(typing.cast(bytes, data.get(b"global_end_time")))
        self.global_que_ans = ByteReader(typing.cast(bytes, data.get(b"global_que_ans")))
        self.global_start_time = ByteReader(typing.cast(bytes, data.get(b"global_start_time")))
        self.global_wallet_address = ByteReader(typing.cast(bytes, data.get(b"global_wallet_address")))


@dataclasses.dataclass(kw_only=True)
class SimulateOptions:
    allow_more_logs: bool = dataclasses.field(default=False)
    allow_empty_signatures: bool = dataclasses.field(default=False)
    extra_opcode_budget: int = dataclasses.field(default=0)
    exec_trace_config: models.SimulateTraceConfig | None         = dataclasses.field(default=None)

class HelloWorldClient:
    """A class for interacting with the HelloWorld app providing high productivity and
    strongly typed methods to deploy and call the app"""

    @typing.overload
    def __init__(
        self,
        algod_client: algosdk.v2client.algod.AlgodClient,
        *,
        app_id: int = 0,
        signer: TransactionSigner | algokit_utils.Account | None = None,
        sender: str | None = None,
        suggested_params: algosdk.transaction.SuggestedParams | None = None,
        template_values: algokit_utils.TemplateValueMapping | None = None,
        app_name: str | None = None,
    ) -> None:
        ...

    @typing.overload
    def __init__(
        self,
        algod_client: algosdk.v2client.algod.AlgodClient,
        *,
        creator: str | algokit_utils.Account,
        indexer_client: algosdk.v2client.indexer.IndexerClient | None = None,
        existing_deployments: algokit_utils.AppLookup | None = None,
        signer: TransactionSigner | algokit_utils.Account | None = None,
        sender: str | None = None,
        suggested_params: algosdk.transaction.SuggestedParams | None = None,
        template_values: algokit_utils.TemplateValueMapping | None = None,
        app_name: str | None = None,
    ) -> None:
        ...

    def __init__(
        self,
        algod_client: algosdk.v2client.algod.AlgodClient,
        *,
        creator: str | algokit_utils.Account | None = None,
        indexer_client: algosdk.v2client.indexer.IndexerClient | None = None,
        existing_deployments: algokit_utils.AppLookup | None = None,
        app_id: int = 0,
        signer: TransactionSigner | algokit_utils.Account | None = None,
        sender: str | None = None,
        suggested_params: algosdk.transaction.SuggestedParams | None = None,
        template_values: algokit_utils.TemplateValueMapping | None = None,
        app_name: str | None = None,
    ) -> None:
        """
        HelloWorldClient can be created with an app_id to interact with an existing application, alternatively
        it can be created with a creator and indexer_client specified to find existing applications by name and creator.
        
        :param AlgodClient algod_client: AlgoSDK algod client
        :param int app_id: The app_id of an existing application, to instead find the application by creator and name
        use the creator and indexer_client parameters
        :param str | Account creator: The address or Account of the app creator to resolve the app_id
        :param IndexerClient indexer_client: AlgoSDK indexer client, only required if deploying or finding app_id by
        creator and app name
        :param AppLookup existing_deployments:
        :param TransactionSigner | Account signer: Account or signer to use to sign transactions, if not specified and
        creator was passed as an Account will use that.
        :param str sender: Address to use as the sender for all transactions, will use the address associated with the
        signer if not specified.
        :param TemplateValueMapping template_values: Values to use for TMPL_* template variables, dictionary keys should
        *NOT* include the TMPL_ prefix
        :param str | None app_name: Name of application to use when deploying, defaults to name defined on the
        Application Specification
            """

        self.app_spec = APP_SPEC
        
        # calling full __init__ signature, so ignoring mypy warning about overloads
        self.app_client = algokit_utils.ApplicationClient(  # type: ignore[call-overload, misc]
            algod_client=algod_client,
            app_spec=self.app_spec,
            app_id=app_id,
            creator=creator,
            indexer_client=indexer_client,
            existing_deployments=existing_deployments,
            signer=signer,
            sender=sender,
            suggested_params=suggested_params,
            template_values=template_values,
            app_name=app_name,
        )

    @property
    def algod_client(self) -> algosdk.v2client.algod.AlgodClient:
        return self.app_client.algod_client

    @property
    def app_id(self) -> int:
        return self.app_client.app_id

    @app_id.setter
    def app_id(self, value: int) -> None:
        self.app_client.app_id = value

    @property
    def app_address(self) -> str:
        return self.app_client.app_address

    @property
    def sender(self) -> str | None:
        return self.app_client.sender

    @sender.setter
    def sender(self, value: str) -> None:
        self.app_client.sender = value

    @property
    def signer(self) -> TransactionSigner | None:
        return self.app_client.signer

    @signer.setter
    def signer(self, value: TransactionSigner) -> None:
        self.app_client.signer = value

    @property
    def suggested_params(self) -> algosdk.transaction.SuggestedParams | None:
        return self.app_client.suggested_params

    @suggested_params.setter
    def suggested_params(self, value: algosdk.transaction.SuggestedParams | None) -> None:
        self.app_client.suggested_params = value

    def get_global_state(self) -> GlobalState:
        """Returns the application's global state wrapped in a strongly typed class with options to format the stored value"""

        state = typing.cast(dict[bytes, bytes | int], self.app_client.get_global_state(raw=True))
        return GlobalState(state)

    def quiz_data(
        self,
        *,
        wallet_address: str,
        booklet: str,
        start_time: str,
        que_ans: str,
        end_time: str,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
    ) -> algokit_utils.ABITransactionResponse[None]:
        """Calls `quiz_data(string,string,string,string,string)void` ABI method
        
        :param str wallet_address: The `wallet_address` ABI parameter
        :param str booklet: The `booklet` ABI parameter
        :param str start_time: The `start_time` ABI parameter
        :param str que_ans: The `que_ans` ABI parameter
        :param str end_time: The `end_time` ABI parameter
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns algokit_utils.ABITransactionResponse[None]: The result of the transaction"""

        args = QuizDataArgs(
            wallet_address=wallet_address,
            booklet=booklet,
            start_time=start_time,
            que_ans=que_ans,
            end_time=end_time,
        )
        result = self.app_client.call(
            call_abi_method=args.method(),
            transaction_parameters=_convert_call_transaction_parameters(transaction_parameters),
            **_as_dict(args, convert_all=True),
        )
        return result

    def create_bare(
        self,
        *,
        on_complete: typing.Literal["no_op"] = "no_op",
        transaction_parameters: algokit_utils.CreateTransactionParameters | None = None,
    ) -> algokit_utils.TransactionResponse:
        """Creates an application using the no_op bare method
        
        :param typing.Literal[no_op] on_complete: On completion type to use
        :param algokit_utils.CreateTransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :returns algokit_utils.TransactionResponse: The result of the transaction"""

        result = self.app_client.create(
            call_abi_method=False,
            transaction_parameters=_convert_create_transaction_parameters(transaction_parameters, on_complete),
        )
        return result

    def clear_state(
        self,
        transaction_parameters: algokit_utils.TransactionParameters | None = None,
        app_args: list[bytes] | None = None,
    ) -> algokit_utils.TransactionResponse:
        """Calls the application with on completion set to ClearState
    
        :param algokit_utils.TransactionParameters transaction_parameters: (optional) Additional transaction parameters
        :param list[bytes] | None app_args: (optional) Application args to pass
        :returns algokit_utils.TransactionResponse: The result of the transaction"""
    
        return self.app_client.clear_state(_convert_transaction_parameters(transaction_parameters), app_args)

    def deploy(
        self,
        version: str | None = None,
        *,
        signer: TransactionSigner | None = None,
        sender: str | None = None,
        allow_update: bool | None = None,
        allow_delete: bool | None = None,
        on_update: algokit_utils.OnUpdate = algokit_utils.OnUpdate.Fail,
        on_schema_break: algokit_utils.OnSchemaBreak = algokit_utils.OnSchemaBreak.Fail,
        template_values: algokit_utils.TemplateValueMapping | None = None,
        create_args: algokit_utils.DeployCallArgs | None = None,
        update_args: algokit_utils.DeployCallArgs | None = None,
        delete_args: algokit_utils.DeployCallArgs | None = None,
    ) -> algokit_utils.DeployResponse:
        """Deploy an application and update client to reference it.
        
        Idempotently deploy (create, update/delete if changed) an app against the given name via the given creator
        account, including deploy-time template placeholder substitutions.
        To understand the architecture decisions behind this functionality please see
        <https://github.com/algorandfoundation/algokit-cli/blob/main/docs/architecture-decisions/2023-01-12_smart-contract-deployment.md>
        
        ```{note}
        If there is a breaking state schema change to an existing app (and `on_schema_break` is set to
        'ReplaceApp' the existing app will be deleted and re-created.
        ```
        
        ```{note}
        If there is an update (different TEAL code) to an existing app (and `on_update` is set to 'ReplaceApp')
        the existing app will be deleted and re-created.
        ```
        
        :param str version: version to use when creating or updating app, if None version will be auto incremented
        :param algosdk.atomic_transaction_composer.TransactionSigner signer: signer to use when deploying app
        , if None uses self.signer
        :param str sender: sender address to use when deploying app, if None uses self.sender
        :param bool allow_delete: Used to set the `TMPL_DELETABLE` template variable to conditionally control if an app
        can be deleted
        :param bool allow_update: Used to set the `TMPL_UPDATABLE` template variable to conditionally control if an app
        can be updated
        :param OnUpdate on_update: Determines what action to take if an application update is required
        :param OnSchemaBreak on_schema_break: Determines what action to take if an application schema requirements
        has increased beyond the current allocation
        :param dict[str, int|str|bytes] template_values: Values to use for `TMPL_*` template variables, dictionary keys
        should *NOT* include the TMPL_ prefix
        :param algokit_utils.DeployCallArgs | None create_args: Arguments used when creating an application
        :param algokit_utils.DeployCallArgs | None update_args: Arguments used when updating an application
        :param algokit_utils.DeployCallArgs | None delete_args: Arguments used when deleting an application
        :return DeployResponse: details action taken and relevant transactions
        :raises DeploymentError: If the deployment failed"""

        return self.app_client.deploy(
            version,
            signer=signer,
            sender=sender,
            allow_update=allow_update,
            allow_delete=allow_delete,
            on_update=on_update,
            on_schema_break=on_schema_break,
            template_values=template_values,
            create_args=_convert_deploy_args(create_args),
            update_args=_convert_deploy_args(update_args),
            delete_args=_convert_deploy_args(delete_args),
        )