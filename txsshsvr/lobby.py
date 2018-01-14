
from __future__ import (
    absolute_import,
    print_function,
)
from txsshsvr import users
import textwrap
from automat import MethodicalMachine


class LobbyProtocol(object):
    _machine = MethodicalMachine()

    # ---------------
    # Protocol states
    # ---------------

    @_machine.state(initial=True)
    def start(self):
        """
        Initial state.
        """
    
    @_machine.state()
    def unjoined(self):
        """
        Avatar has not joined a group session yet. 
        """

    @_machine.state()
    def waiting_for_accepts(self):
        """
        User has invited others to a session, is waiting for them to accept.
        May still cancel invite at this point.
        """

    @_machine.state()
    def invited(self):
        """
        User has been invited to a session.
        May accept or reject.
        """

    @_machine.state()
    def accepted(self):
        """
        User has accepted invitation to a session.  
        Is waiting for session to start.
        May still withdraw from invitation at this point.
        """ 

    @_machine.state()
    def session_started(self):
        """
        The session has started.
        A new protcol can take over at this point.
        """

    # ------
    # Inputs
    # ------
   
    @_machine.input()
    def initialize(self):
        """
        Initialize the machine.
        """

    @_machine.input()
    def send_invitations(self):
        """
        Send invitations to other users.
        """

    @_machine.input()
    def received_invitation(self):
        """
        Received an invitation to join a session.
        """

    @_machine.input()
    def received_accepts(self):
        """
        Received acceptances to all invitations sent.
        """

    @_machine.input()
    def cancel(self):
        """
        Cancel an invitation or an acceptance.
        """

    @_machine.input()
    def accept(self):
        """
        Accept an invitation.
        """

    @_machine.input()
    def reject(self):
        """
        Reject an invitation.
        """

    @_machine.input()
    def start_session(self):
        """
        Start a session.
        """

    # -------
    # Outputs
    # -------

    @_machine.output()
    def _enter_unjoined(self):
        self.handle_unjoined()

    @_machine.output()
    def _enter_invited(self):
        self.handle_invited()

    @_machine.output()
    def _enter_accepted(self):
        self.handle_accepted()

    @_machine.output()
    def _enter_waiting_for_accepts(self):
        self.handle_waiting_for_accepts()

    @_machine.output()
    def _enter_session_started(self):
        self.handle_session_started()

    @_machine.output()
    def _enter_invited(self):
        self.handle_invited()

    # --------------
    # Event handlers
    # --------------

    def handle_unjoined(self):
        raise NotImplementedError()
    
    def handle_invited(self):
        raise NotImplementedError()
    
    def handle_accepted(self):
        raise NotImplementedError()
    
    def handle_waiting_for_accepts(self):
        raise NotImplementedError()
    
    def handle_session_started(self):
        raise NotImplementedError()
    
    def handle_invited(self):
        raise NotImplementedError()
    
    # -----------
    # Transitions
    # -----------
    start.upon(initialize, enter=unjoined, outputs=[_enter_unjoined])
    unjoined.upon(send_invitations, enter=waiting_for_accepts, outputs=[_enter_unjoined])
    unjoined.upon(received_invitation, enter=invited, outputs=[_enter_invited])
    waiting_for_accepts.upon(received_accepts, enter=session_started, outputs=[_enter_session_started])
    waiting_for_accepts.upon(cancel, enter=unjoined, outputs=[_enter_unjoined])
    invited.upon(accept, enter=accepted, outputs=[_enter_accepted])
    invited.upon(reject, enter=unjoined, outputs=[_enter_unjoined])
    accepted.upon(start_session, enter=session_started, outputs=[_enter_session_started])
    accepted.upon(cancel, enter=unjoined, outputs=[_enter_unjoined])


class SSHLobbyProtocol(LobbyProtocol):
    prompt = "$"

    def __init__(self, terminal):
        self._terminal = terminal
        self.valid_commands = {}

    def handle_unjoined(self):
        terminal = self._terminal
        terminal.cursorHome()
        terminal.eraseLine()
        terminal.write(
            "STATUS: {}, you are not part of any session.".format(
                self.avatar.user_id))
        terminal.nextLine()
        msg = textwrap.dedent("""\
        Valid commands are:
        * invite player[, player ...] - Invite players to join a session.
        * list                        - List players in the lobby. 
        """)
        self.valid_commands = {
            'list': self._list_players,
        }
        terminal.write(msg)
        self.show_prompt()
    
    def handle_invited(self):
        pass
    
    def handle_waiting_for_accepts(self):
        pass
    
    def handle_session_started(self):
        pass
    
    def handle_invited(self):
        pass

    def handle_accepted(self):
        pass

    def show_prompt(self):
        self._terminal.write("{0} ".format(self.prompt))

    def handle_line(self, line):
        """
        Parse user input and act on commands.
        """
        line = line.strip()
        if line == "":
            return
        words = line.split()
        command = words[0].lower()
        args = words[1:]
        func = self.valid_commands.get(command, lambda args: self._invalid_command(words))
        func(args)
        self.show_prompt()

    def _list_players(self, args):
        """
        List players.
        """
        user_ids = users.get_user_ids()
        for user_id in user_ids:
            self._terminal.write(user_id)
            self._terminal.nextLine()
        
    def _invalid_command(self, args):
        """
        Command entered was invalid.
        """
        self._terminal.write("Invalid command: {}".format(args[0]))
        self._terminal.nextLine()

