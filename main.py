from textual.app import App, ComposeResult
from textual.coordinate import Coordinate
from textual.screen import ModalScreen, Screen
from textual.widgets import Collapsible, Label, Header, DataTable, Input, Button
from textual.containers import Grid
from rich.text import Text
from bonusly import check_balance

ROWS = [
    ('Name', 'Bonusly Name (first.last)', 'Wager Amount', 'Value in Chips', '', ''),
    ('Jackson', 'jackson.barton', 100, 1000, 'VERIFIED', 'EDIT'),
    ('Isaac', 'isaac.picton', 100, 1000, 'PENDING', 'EDIT'),
]

CHIP_SCALING = 10


class MainScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header()
        with Collapsible(title='Game setup', collapsed=False):
            yield DataTable()

    def on_button_pressed(self) -> None:
        self.exit()

    def on_mount(self) -> None:
        self.title = "Pokusly"
        self.sub_title = "The Bonusly Payout app for Poker"
        self.table = self.query_one(DataTable)
        self.draw_table()
        

    def on_data_table_cell_selected(self, event):
        if event.coordinate.column == 4:
            row = self.table.get_row_at(event.coordinate.row)
            verified = check_balance(row[1], row[2])
            if (verified): 
                self.table.update_cell_at(event.coordinate, Text(str('VERIFIED'), style='#2dc937', justify='center'))
            else:
                self.table.update_cell_at(event.coordinate, Text(str('FAILED'), style='#cc3232', justify='center'))
        elif event.coordinate.column == 5:
            # Selected EDIT
            row = self.table.get_row_at(event.coordinate.row)
            self.app.push_screen(EditCellScreen(row[0], row[1], row[2]))
        # self.draw_table()

    def draw_table(self) -> None:
        self.column_keys = self.table.add_columns(*ROWS[0])
        self.row_keys = []
        for row in ROWS[1:]:
            verification_color = ''
            match row[4]:
                case 'VERIFIED':
                    verification_color = '#2dc937'
                case 'PENDING':
                    verification_color = '#e7b416'
                case 'FAILED':
                    verification_color = '#cc3232'
            
            styled_row = [
                row[0], row[1], row[2], row[3], Text(str(row[4]), style=verification_color, justify='center'), Text(str(row[5]), style='#e7b416', justify='center')
            ]
            self.row_keys.append(self.table.add_row(*styled_row))
        self.row_keys.append(self.table.add_row('', '', '', '', '', Text(str('ADD'), style='#2dc937', justify='center')))


class EditCellScreen(ModalScreen):
    def __init__(
        self,
        player_name = '', bonusly_name = '', wager = 0,
        name = None, id = None, classes = None
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.player_name = player_name
        self.bonusly_name = bonusly_name
        self.wager = wager

    def compose(self) -> ComposeResult:
        yield Grid(
            Label('Player Name'),
            Input(id='player_name'),
            Label('Bonuly Username (first.last)'),
            Input(id='bonusly_name'),
            Label('No. Points to Wager'),
            Input(id='wager'),
            Button('Submit', variant='success', id='submit'),
            Button("Cancel", variant="primary", id="cancel"),
            id='dialog'
        )

    def on_mount(self) -> None:
        player_name_input = self.query_one('#player_name', Input)
        player_name_input.value = str(self.player_name)
        bonusly_name_input = self.query_one('#bonusly_name', Input)
        bonusly_name_input.value = str(self.bonusly_name)
        wager_input = self.query_one('#wager', Input)
        wager_input.value = str(self.wager)

        player_name_input.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:

        if event.button.id == 'submit':
            player_name_input = self.query_one('#player_name', Input)
            new_player_name = player_name_input.value
            bonusly_name_input = self.query_one('#bonusly_name', Input)
            new_bonusly_name = bonusly_name_input.value
            wager_input = self.query_one('#wager', Input)
            new_wager = wager_input.value

            if (new_player_name != '' and new_bonusly_name != '' and new_wager.isdigit()):

                main_screen = self.app.get_screen("main")

                table = main_screen.query_one(DataTable)

                if (new_player_name != self.player_name):
                    table.update_cell_at(
                        Coordinate(table.cursor_coordinate.row, 0),
                        new_player_name,
                        update_width=True
                    )

                if (new_bonusly_name != self.bonusly_name):
                    table.update_cell_at(
                        Coordinate(table.cursor_coordinate.row, 1),
                        new_bonusly_name,
                        update_width=True
                    )
                    table.update_cell_at(
                        Coordinate(table.cursor_coordinate.row, 4),
                        Text(str('PENDING'), style='#e7b416', justify='center'),
                    )

                if (new_wager != self.wager):
                    table.update_cell_at(
                        Coordinate(table.cursor_coordinate.row, 2),
                        new_wager,
                        update_width=True
                    )
                    table.update_cell_at(
                        Coordinate(table.cursor_coordinate.row, 4),
                        Text(str('PENDING'), style='#e7b416', justify='center'),
                    )
                    table.update_cell_at(
                        Coordinate(table.cursor_coordinate.row, 3),
                        int(new_wager) * CHIP_SCALING,
                        update_width=True
                    )
                
                if (str(table.get_cell_at(table.cursor_coordinate)) == 'ADD'):
                    table.update_cell_at(
                        table.cursor_coordinate,
                        Text(str('EDIT'), style='#e7b416', justify='center'),
                        update_width=True
                    )
                    table.add_row('', '', '', '', '', Text(str('ADD'), style='#2dc937', justify='center'))

        self.app.pop_screen()


class QuitScreen(ModalScreen):
    """Screen with a dialog to quit."""

    def compose(self) -> ComposeResult:
        yield Grid(
            Label("Are you sure you want to quit?", id="question"),
            Button("Quit", variant="error", id="quit"),
            Button("Cancel", variant="primary", id="cancel"),
            id="quitdialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "quit":
            self.app.exit()
        else:
            self.app.pop_screen()

class Pokusly(App):
    SCREENS = {"main": MainScreen}
    CSS_PATH = "pokusly.tcss"
    BINDINGS = [("q", "request_quit", "Quit")]

    def on_mount(self) -> None:
        self.push_screen("main")

    def action_request_quit(self) -> None:
        """Action to display the quit dialog."""
        self.push_screen(QuitScreen())

def main():
    app = Pokusly()
    app.run()

if __name__ == "__main__":
    main()

    