"""Types for jyge messages."""
from typing import Any, Dict, List, Literal, TypedDict, Union

AnyContent = Union[Dict[str, Any], str, Union[int, float], bool, None, None]


MessageTypeAppInfo = Literal["app_info"]


MessageTypeRun = Literal["run"]


AnyMessageType = Union[MessageTypeRun, MessageTypeAppInfo]


class AppInfoRequest(TypedDict, total=False):
    """app info request."""

    content: AnyContent
    request_id: str
    request_type: MessageTypeAppInfo


class RunRequestContent(TypedDict, total=False):
    """run request content."""

    args: Dict[str, Any]
    id: str


class RunRequest(TypedDict, total=False):
    """run request."""

    content: RunRequestContent
    request_id: str
    request_type: MessageTypeRun


AnyRequest = Union[AppInfoRequest, RunRequest]


class CommandInfo(TypedDict, total=False):
    """command info."""

    caption: str
    className: str
    dataset: Dict[str, Any]
    icon: Union[str, None]
    iconClass: str
    iconLabel: str
    isEnabled: bool
    isToggleable: bool
    isToggled: bool
    isVisible: bool
    label: str
    mnemonic: Union[str, Union[int, float]]
    usage: str


CommandsInfo = Dict[str, CommandInfo]


class AppInfo(TypedDict, total=False):
    """app info."""

    commands: CommandsInfo
    name: str
    plugins: List[str]
    title: str
    url: str
    version: str


class AppInfoResponse(TypedDict, total=False):
    """app info response."""

    content: AppInfo
    request_id: str
    request_type: MessageTypeAppInfo


class RunResponse(TypedDict, total=False):
    """run response."""

    content: AnyContent
    request_id: str
    request_type: MessageTypeAppInfo


AnyValidResponse = Union[AppInfoResponse, RunResponse]


class ErrorResponse(TypedDict, total=False):
    """error response."""

    error: str
    request_id: str
    request_type: AnyMessageType


AnyResponse = Union[AnyValidResponse, ErrorResponse]


AnyMessage = Union[AnyRequest, AnyResponse]
