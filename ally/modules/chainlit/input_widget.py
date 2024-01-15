from typing import Any, Dict, Optional

from chainlit.input_widget import InputWidget
from chainlit.types import InputWidgetType
from pydantic.dataclasses import dataclass


@dataclass
class TextInput(InputWidget):
	"""Useful to create a text input."""

	type: InputWidgetType = "textinput"
	initial: Optional[str] = None
	placeholder: Optional[str] = None
	multiline: bool = False

	def to_dict(self) -> Dict[str, Any]:
		return {
			"type": self.type,
			"id": self.id,
			"label": self.label,
			"initial": self.initial,
			"placeholder": self.placeholder,
			"tooltip": self.tooltip,
			"description": self.description,
			"multiline": self.multiline,
		}