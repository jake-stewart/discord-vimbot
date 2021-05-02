import subprocess

def run_command(command):
    return subprocess.Popen(
        command,
        stdout=subprocess.PIPE
    ).communicate()[0].decode()


class Term:
    def __init__(self, session_name, command="bash"):
        self.cursor = "█"
        self.draw_cursor = True
        self.session_name = session_name
        self.shortcuts = {
            "esc": "Escape",
            "space": " ",
            "cr": "Enter",
            "bs": "Bspace",
            "tab": "Tab",
            "up": "Up",
            "left": "Left",
            "down": "Down",
            "right": "Right",
        }

        # kill previous terminal session if still running
        self.end()

        run_command(
            ["tmux", "new-session", "-d", "-s", f"{self.session_name}", "-c", "/home/user", f"sudo -i -u user {command}"]
        )

    def toggle_cursor(self):
        if self.draw_cursor:
            self.draw_cursor = False
            return
        self.draw_cursor = True

    def get_screen(self):
        # get a view of the terminal session and convert to array of lines
        screen = run_command(
            ["tmux", "capture-pane", "-J", "-pt", f"{self.session_name}"]
        ).split('\n')

        if screen == ['']:
            return 0

        index = 0
        while True:
            line = screen[index].rstrip()

            # wrap long lines
            if len(line) > 79:
                while True:
                    fixed, line = line[:80], line[80:]
                    screen[index] = fixed
                    if not len(line):
                        break
                    index += 1
                    screen.insert(index, line)
                    if len(line) <= 79:
                        break

            # fill empty lines with a space so that discord shows them
            elif line == '':
                screen[index] = ' '

            index += 1
            if index == len(screen):
                break

        if self.draw_cursor:
            # get cursor position
            x, y = run_command(
                ["tmux", "display-message", "-p", "-t", f"{self.session_name}", "-F", "#{cursor_x} #{cursor_y}"]
            ).split()
            x, y = int(x), int(y)

            # draw cursor to screen
            screen[y] = screen[y][:x] + self.cursor + screen[y][x + 1:]

        # return the screen array as a string
        return '\n'.join(screen)


    def send_command(self, command):
        run_command(
            ["tmux", "send-keys", "-t", f"{self.session_name}", f"{command}"]
       )

    def send_text(self, text):
        run_command(
            ["tmux", "send-keys", "-l", "-t", f"{self.session_name}", f"{text}"]
       )

    def send_keys(self, keys):
        parsing = ''
        for key in keys:
            if key == '<':
                if parsing:
                    self.send_text(parsing)
                parsing = '<'
            elif key == '>':
                parsing += '>'
                command = parsing[1:-1].lower()
                if command.startswith('c-') and len(command) == 3:
                    self.send_command(command)
                elif command in self.shortcuts:
                    self.send_command(self.shortcuts[command])
                else:
                    self.send_text(parsing)
                parsing = ''
            else:
                parsing += key

        if parsing:
            self.send_text(parsing)


    def end(self):
        run_command(["tmux", "kill-session", "-t", f"{self.session_name}"])
