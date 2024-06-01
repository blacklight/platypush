import os
from dataclasses import dataclass
from datetime import datetime as dt
from enum import Enum
from threading import RLock
from typing import IO, Iterable, List, Optional

import requests

from platypush.plugins import Plugin, action


class ContextEntryRole(Enum):
    """
    Roles for context entries.
    """

    ASSISTANT = "assistant"
    SYSTEM = "system"
    USER = "user"


@dataclass
class ContextEntry:
    """
    A context entry.
    """

    timestamp: dt
    role: ContextEntryRole
    content: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            timestamp=dt.fromisoformat(data.get("timestamp", dt.now().isoformat())),
            role=ContextEntryRole(data["role"]),
            content=data["content"],
        )

    def to_dict(self):
        return {
            "role": self.role.value,
            "content": self.content,
        }


class OpenaiPlugin(Plugin):
    """
    Plugin to interact with OpenAI services.

    Currently supported:

        - :meth:`get_response`: Get a response to a prompt/question using the
          GPT API. It supports custom contexts and environment settings.

        - :meth:`transcribe`: Perform speech-to-text on an audio file. This API
          is also leveraged by the
          :class:`platypush.plugins.assistant.openai.OpenaiPlugin` to provide a
          full-fledged voice assistant.

        - Through the :class:`platypush.plugins.tts.openai.OpenaiPlugin` plugin,
          text-to-speech is also supported.

    Contexts
    --------

    The plugin also supports the implementation of custom assistant
    *contexts*/environment.

    Contexts can be used to:

        - Customize the model's behavior based on a set of inputs - going from
          a generic "*You are a helpful assistant*" to a more specific "*You
          are a Star Trek fan*", or "*You are a 16th century noble lady who
          talks in Shakespearean English to her peers*".
        - Pre-configure the model with a set of previous interactions in order
          to either pre-load information that we expect the model to remember,
          or to provide a set of previous interactions that the model can use
          to generate responses that are consistent with the conversation
          history.

    The plugin provides two types of contexts:

        - **Default context**: This is a set of context entries that are
          provided at plugin initialization and that will be used to initialize
          the model with a configuration or set of previous interactions that
          will be remembered when generating all responses.

        - **Runtime context**: This is a set of context entries that can be
          passed at runtime at :meth:`.get_response`. All the interactions
          (both user prompts and assistant responses) that are processed
          through :meth:`.get_response` will also be added to the runtime
          context, and remembered for the next ``context_expiry`` seconds. This
          allows you to generate responses that are consistent with the recent
          conversation history.

    Each context entry is a dictionary with the following keys:

        - ``role``: The role of the message. Can be one of:
            - ``system``: A system message provided to the model to set
              up its initial state - e.g. "you are a helpful
              assistant".
            - ``user``: A user message, as provided by a previous (real
              or synthetic) user interaction.
            - ``assistant``: An assistant message, as provided by a
              previous (real or synthetic) assistant response.
        - ``content``: The content of the message.

    An example of context:

      .. code-block:: yaml

        context:
            - role: system
              content: >
                  You are a 16th century noble lady who talks in
                  Shakespearean English to her peers.
            - role: user
              content: What is a telephone?
            - role: assistant
              content: >
                  Pray tell, noble companion, a telephone is a device
                  of modern innovation that doth permit one to speak
                  with a distant acquaintance by means of magical pink
                  waves that do carry the sound of thine voice to the
                  ear of the listener.

    Given such context, if you call :meth:`.get_response` with a
    prompt such as "*How does it work?*", the model may generate a
    response such as "*Fair lady, to use a telephone, thou must first
    lift the receiver and place it to thine ear. Then, thou must speak
    into the mouthpiece as though conversing with a companion in
    another room. The magical pink waves shall carry thy words to the
    recipient, who shall hear them on their own device. 'Tis a wondrous
    invention indeed!*".

    Note that the model will remember the previous interactions and
    also generate responses, so you can ask it direct questions such as "How
    does it work" while remembering what "it" is likely to mean. And it'll
    provide responses which are in the same style initialized through the
    ``system`` context.
    """

    def __init__(
        self,
        api_key: Optional[str],
        model: str = "gpt-3.5-turbo",
        timeout: float = 30,
        context: Optional[Iterable[dict]] = None,
        context_expiry: Optional[float] = 600,
        max_tokens: int = 500,
        **kwargs,
    ):
        """
        :param api_key: OpenAI API key. If not set, it will be read from the
            ``OPENAI_API_KEY`` environment variable.
        :param model: The model to use. Default: ``gpt-3.5-turbo``.
        :param timeout: Default timeout for API requests (default: 30 seconds).
        :param max_tokens: Maximum number of tokens to generate in the response
            (default: 500).
        :param context: Default context to use for completions, as a list of
            dictionaries with ``role`` and ``content`` keys. Default: None.
        :param context_expiry: Default expiry time for the context in seconds.
            After this time since the last interaction, the context will be
            cleared.

            This means that any follow-up interactions happening within the
            expiry window will remember the past prompts, but any interaction
            that happens after the expiry window (calculated from the time of
            the last interaction) will start fresh.

            Note that ``context_expiry`` is only applied to the runtime
            context. The default context will never expire unless it's removed
            from the plugin configuration.

            Set to 0 to disable context expiry - i.e. all messages stay in the
            context until the plugin is restarted or the context is cleared
            explicitly via :meth:`.clear_context`. Default: 600 seconds (10
            minutes).
        """
        super().__init__(**kwargs)
        api_key = api_key or os.getenv('OPENAI_API_KEY')
        assert api_key, 'OpenAI API key not provided'

        self._api_key = api_key
        self._context_lock = RLock()
        self._runtime_context: List[ContextEntry] = []
        self._default_context = [
            ContextEntry.from_dict(entries) for entries in (context or [])
        ]

        self.max_tokens = max_tokens
        self.context_expiry = context_expiry
        self.model = model
        self.timeout = timeout

    def _rotate_context(self):
        """
        Rotate the context by removing any entries older than the configured
        ``context_expiry``.
        """
        if not self.context_expiry:
            return

        with self._context_lock:
            now = dt.now()
            self._runtime_context = [
                entry
                for entry in self._runtime_context
                if (now - entry.timestamp).total_seconds() < self.context_expiry
            ]

    @action
    def get_response(
        self,
        prompt: str,
        model: Optional[str] = None,
        context: Optional[Iterable[dict]] = None,
        timeout: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Optional[str]:
        """
        Get completions for a given prompt using ChatGPT.

        :param prompt: The prompt/question to complete/answer.
        :param model: Override the default model to use.
        :param context: Extend the default context with these extra messages.
        :param max_tokens: Override the default maximum number of tokens to
            generate in the response.
        :param timeout: Override the default timeout for the API request.
        :return: The completion for the prompt - or, better, the message
            associted to the highest scoring completion choice.
        """
        self._rotate_context()
        context = [
            *(context or []),
            {
                "role": "user",
                "content": prompt,
            },
        ]

        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            timeout=timeout or self.timeout,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model or self.model,
                "messages": [
                    *(
                        entry.to_dict()
                        for entry in (
                            *(self._default_context or []),
                            *self._runtime_context,
                        )
                    ),
                    *context,
                ],
                "max_tokens": max_tokens or self.max_tokens,
            },
        )

        resp.raise_for_status()
        self._update_context(*context)
        choices = resp.json()["choices"]
        self.logger.debug("OpenAI response: %s", resp.json())

        if not choices:
            return None

        msg = choices[0]["message"]
        self._update_context(msg)
        return msg["content"]

    def _process_transcribe_response(self, resp: requests.Response) -> str:
        rs_json = None

        try:
            rs_json = resp.json()
        except Exception:
            pass

        self.logger.debug("OpenAI response: %s", rs_json)
        resp.raise_for_status()
        return (rs_json or {}).get("text", "")

    def transcribe_file(
        self,
        f: IO,
        model: Optional[str] = 'whisper-1',
        timeout: Optional[float] = None,
    ) -> str:
        resp = requests.post(
            "https://api.openai.com/v1/audio/transcriptions",
            timeout=timeout or self.timeout,
            headers={
                "Authorization": f"Bearer {self._api_key}",
            },
            files={
                "file": f,
            },
            data={
                "model": model or self.model,
            },
        )

        return self._process_transcribe_response(resp)

    def transcribe_raw(
        self,
        audio: bytes,
        extension: str,
        model: Optional[str] = 'whisper-1',
        timeout: Optional[float] = None,
    ) -> str:
        resp = requests.post(
            "https://api.openai.com/v1/audio/transcriptions",
            timeout=timeout or self.timeout,
            headers={
                "Authorization": f"Bearer {self._api_key}",
            },
            files={
                "file": (f"audio.{extension}", audio),
            },
            data={
                "model": model or self.model,
            },
        )

        return self._process_transcribe_response(resp)

    @action
    def transcribe(
        self,
        audio: str,
        model: Optional[str] = 'whisper-1',
        timeout: Optional[float] = None,
    ) -> str:
        """
        Perform speech-to-text on an audio file.

        :param audio: The audio file to transcribe.
        :param model: The model to use for speech-to-text. Default:
            ``whisper-1``. If not set, the configured default model will be
            used.
        :param timeout: Timeout for the API request. If not set, the default
            timeout will be used.
        :return: The transcribed text.
        """
        with open(os.path.expanduser(audio), "rb") as f:
            return self.transcribe_file(f, model=model, timeout=timeout)

    def _update_context(self, *entries: dict):
        """
        Update the context with a new entry.
        """
        with self._context_lock:
            for entry in entries:
                self._runtime_context.append(ContextEntry.from_dict(entry))
            self._rotate_context()

    @action
    def clear_context(self):
        """
        Clear the runtime context.
        """
        with self._context_lock:
            self._runtime_context = []
