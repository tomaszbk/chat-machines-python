import textwrap

from pydantic import BaseModel, ConfigDict


class State:
    _registry: list = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._registry.append(cls)

    def on_enter(session):
        pass

    def on_update(session):
        pass

    def on_exit(session):
        pass


class ChangeState(Exception):
    """Exception to signal a state change in the state machine."""

    pass


class SessionState(BaseModel):
    input: str
    output: str = ""
    next_state: State = None
    data: object = None
    _end_session: bool = False
    _current_state: State = None

    def add_output(self, output: str):
        """Adds output to the session's output."""
        self.output += f"{textwrap.dedent(output).strip()}\n"

    def change_state(self, state: State):
        self.next_state = state
        raise ChangeState()

    def end(self):
        self._end_session = True

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ChatMachine:
    """A generic state machine."""

    sessions: dict[str, SessionState] = {}

    def __init__(self, start_state: State = None):
        """
        Initializes the state machine.
        """
        self.states = State._registry
        self.start_state = start_state
        self._global_on_enter_hook = lambda session: None
        self._global_on_update_hook = lambda session: None
        self._global_on_exit_hook = lambda session: None

    def global_on_enter(self, fn):
        """
        Decorator to register a global on_enter hook.
        Usage:
            @state_machine.global_on_enter
            def my_hook(session: SessionState):
                ...
        """
        self._global_on_enter_hook = fn
        return fn

    def global_on_update(self, fn):
        """
        Decorator to register a global on_update hook.
        Usage:
            @state_machine.global_on_update
            def my_hook(session: SessionState):
                ...
        """
        self._global_on_update_hook = fn
        return fn

    def global_on_exit(self, fn):
        """
        Decorator to register a global on_exit hook.
        Usage:
            @state_machine.global_on_exit
            def my_hook(session: SessionState):
                ...
        """
        self._global_on_exit_hook = fn
        return fn

    @classmethod
    def get_session(cls, session_id: str) -> SessionState:
        """Returns the current session state."""
        if session_id not in cls.sessions:
            cls.sessions[session_id] = SessionState(input="", output="")
        return cls.sessions[session_id]

    def run(self, input: str, session_id: str):
        session = self.get_session(session_id)
        session.input = input
        session.output = ""

        try:
            if not session._current_state:
                session._current_state = self.start_state
                self._global_on_enter_hook(session)
                session._current_state.on_enter(session)
            else:
                session._current_state.on_update(session)
        except ChangeState:
            session._current_state.on_exit(session)
            session._current_state = session.next_state
            session.next_state = None
            self._global_on_enter_hook(session)
            session._current_state.on_enter(session)
        output = session.output
        if session._end_session:
            del self.sessions[session_id]
        return output
