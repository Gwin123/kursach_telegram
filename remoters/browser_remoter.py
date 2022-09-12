import webbrowser

from browser_history.browsers import OperaGX, Edge, Firefox, Brave, Chromium, Opera, Safari, Chrome


class BrowserRemote:
    def __init__(self):
        self.browsers = [OperaGX, Edge, Firefox, Brave, Chromium, Opera, Safari, Chrome]

    def get_history(self, date):
        all_history = f'История браузеров на {date}, вы можете указать дату в формате комманды \n' \
                      f'/history 2022-08-10 \n'
        for browser in self.browsers:
            try:
                br = browser()
                output_history = br.fetch_history()

                history = output_history.histories

                browser_his = ""
                for h in history:
                    if str(h[0].date()) == date:
                        browser_his += h[1] + '\n\n'

                if browser_his:
                    all_history += f"История {br.name} \n" + browser_his
                else:
                    all_history += f"История {br.name} на {date} пуста \n"

            except FileNotFoundError:
                all_history += f"{browser.name} браузер не найден \n"
            except AssertionError:
                all_history += f"{browser.name} браузер не поддерживается ОС \n"

        return all_history

    def open_url(self, url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"):
        webbrowser.open(url, new=1)
