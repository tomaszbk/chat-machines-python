import random

from loguru import logger
from pydantic import BaseModel

from chatmachine import ChatMachine, SessionState, State

HANGMAN_PICS = [
    """
  +---+
      |
      |
      |
     ===""",
    """
  +---+
  O   |
      |
      |
     ===""",
    """
  +---+
  O   |
  |   |
      |
     ===""",
    """
  +---+
  O   |
 /|   |
      |
     ===""",
    """
  +---+
  O   |
 /|\\  |
      |
     ===""",
    """
  +---+
  O   |
 /|\\  |
 /    |
     ===""",
    """
  +---+
  O   |
 /|\\  |
 / \\  |
     ===""",
]

WORD_LIST = [
    "python",
    "programacion",
    "ahorcado",
    "desarrollo",
    "computadora",
    "terminal",
    "juego",
    "codigo",
]


def choose_word():
    return random.choice(WORD_LIST).upper()


class GameData(BaseModel):
    correct_letters: set[str] = set()
    wrong_letters: set[str] = set()
    wrong_guesses: int = 0
    secret_word: str = ""


def display_state(session):
    data: GameData = session.data
    session.output += HANGMAN_PICS[data.wrong_guesses] + "\n"
    display_word = " ".join(
        [c if c in data.correct_letters else "_" for c in data.secret_word]
    )
    session.output += f"Palabra: {display_word}"
    session.output += f"\nLetras usadas: {', '.join(sorted(data.correct_letters | data.wrong_letters))}\n"

    session.output += f"Errores: {data.wrong_guesses}/{len(HANGMAN_PICS) - 1}\n"


def input_letter(session: SessionState):
    already_guessed = session.data.correct_letters | session.data.wrong_letters
    letter = session.input.upper()
    if len(letter) != 1 or not letter.isalpha():
        session.output += "letra no valida."
    elif letter in already_guessed:
        session.output += "Ya has usado esa letra. Prueba otra."
    else:
        return letter


class MENU(State):
    def on_enter(session: SessionState):
        session.add_output("""
        Hola! que desea hacer?
        1- Ahorcado
        2- Salir
        """)

    def on_update(session: SessionState):
        if session.input == "1":
            session.change_state(HANGMAN)
        elif session.input == "2":
            session.output += "Gracias por utilizarme"
            session.end()


class HANGMAN(State):
    def on_enter(session: SessionState):
        session.data = GameData()
        session.data.secret_word = choose_word()
        display_state(session)
        session.output += "Ingrese una letra"

    def on_update(session: SessionState):
        data: GameData = session.data
        letter = input_letter(session)
        if not letter:
            return
        if letter in data.secret_word:
            data.correct_letters.add(letter)
            display_state(session)
            if all(c in data.correct_letters for c in data.secret_word):
                session.output += (
                    f"¡Felicidades! Has adivinado la palabra: {data.secret_word}"
                )
                session.change_state(GAME_END)
        else:
            data.wrong_letters.add(letter)
            data.wrong_guesses += 1
            display_state(session)
            if data.wrong_guesses == len(HANGMAN_PICS) - 1:
                session.output += f"¡Has perdido! La palabra era: {data.secret_word}"
                session.change_state(GAME_END)


class GAME_END(State):
    def on_enter(session: SessionState):
        session.output += "Gracias por jugar.\n"
        session.output += "Jugar de nuevo? (S/N)"

    def on_update(session: SessionState):
        input = session.input.upper()
        if input == "S":
            session.change_state(HANGMAN)
        elif input == "N":
            session.output += "Gracias por jugar."
            session.end()
        else:
            session.output += "Opción inválida."


hangman_state_machine = ChatMachine(start_state=MENU)


@hangman_state_machine.global_on_enter
def global_on_enter(session: SessionState):
    logger.info(f"Entrando al estado {session._current_state.__name__}")
