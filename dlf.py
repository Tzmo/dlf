import ssl, tempfile, time, uuid, argparse, shutil, glob, threading, math, os, sys, requests, urllib3, colorama, hashlib
from hurry.filesize import size

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
ssl._create_default_https_context = ssl._create_unverified_context
colorama.init()


class DownloadFile:
    def __init__(self, url=None, chunk_size=0.5, max_threads=20, filename=None, save_path=f"{sys.path[0]}\\dlf", show_info=False, clean=False):
        self.url = url
        self.filename = filename or ".".join(self.url.split("/")[-1].split(".")[:-1])
        self.extention = url.split("/")[-1].split("?")[0].split(".")[-1] or ""
        self.filename_all = filename + "." + self.extention or url.split("/")[-1].split("?")[0]
        self.uuid = uuid.uuid4()
        self.hash = hashlib.md5(url.encode()).hexdigest()
        self.chunk_size = chunk_size
        self.save_path = save_path
        self.temp_folder = f"{tempfile.gettempdir()}\\dlf-temp-folder"
        self.file_size = self.get_file_size()
        self.file_size_clean = size(self.file_size)
        self.number_of_parts = self.get_number_of_parts()
        self.downloaded_parts = 0
        self.clean = clean
        self.parts = self.get_downloaded_parts() or []
        self.chunk_list = self.get_chunk_list()
        self.start_time = time.time()
        self.end_time = None
        self.show_info = show_info
        self.thread_lock = threading.Lock()
        self.session = requests.Session()

        self.threads = []
        self.max_threads = max_threads
        self.thread_number = 0

        self.create_folders()
        self.start()


    def output(self, msg):
        with self.thread_lock:
            print(msg)

    
    def create_folders(self):
        if not os.path.exists(f"{self.save_path}"):
            os.mkdir(f"{self.save_path}")
        if not os.path.exists(f"{self.temp_folder}"):
            os.mkdir(f"{self.temp_folder}")
        if not os.path.exists(f"{self.temp_folder}\\{self.hash}"):
            os.mkdir(f"{self.temp_folder}\\{self.hash}")


    def get_file_size(self):
        req = requests.head(self.url, allow_redirects=True, verify=False)
        byte_size = int(req.headers['Content-Length'])
        return byte_size

    
    def get_number_of_parts(self):
        return int(math.ceil(self.file_size/(1048576 * self.chunk_size)))

    
    def get_downloaded_parts(self):
        if self.clean: return []
        return [f.split("\\")[-1] for f in glob.glob(f"{self.temp_folder}\\{self.hash}\\*")]


    # https://stackoverflow.com/questions/63008887/downloading-files-in-chunks-in-python/63009332#63009332
    def get_chunk_list(self):
        part_duration = math.ceil(self.file_size / self.number_of_parts)
        return [(start, min(start + part_duration - 1, self.file_size - 1)) 
                for start in range(0, self.file_size, part_duration)]

    
    def percentage(self):
        percentage = 100 * float(self.downloaded_parts)/float(self.number_of_parts)
        percentage = round(percentage, 2)
        return str(percentage) + "%"

    
    def download_part(self, headers, part_number, thn):
        while True:
            try:
                rsp = self.session.get(self.url, headers=headers, allow_redirects=True, timeout=1, verify=False)
                if rsp.status_code in [200, 206]:
                    with open(f"{self.temp_folder}\\{self.hash}\\{part_number:05d}", "wb") as f:
                        f.write(rsp.content)
                        f.close()
                    self.downloaded_parts += 1
                    self.parts.append(str(f"{part_number:05d}"))
                    if self.show_info: self.output(f"{colorama.Fore.WHITE}[{colorama.Fore.CYAN}{self.percentage()}{colorama.Fore.WHITE}]-[{colorama.Fore.CYAN}{self.downloaded_parts}/{self.number_of_parts}{colorama.Fore.WHITE}]-[{colorama.Fore.CYAN}{headers['Range']}{colorama.Fore.WHITE}]")
                    self.threads.remove(thn)
                    break
                else:
                    time.sleep(0.1)
            except Exception as e:
                if self.show_info: print(e)
                time.sleep(0.1)


    def start(self):
        for i, (start, end) in enumerate(self.chunk_list):
            while len(self.threads) > self.max_threads:
                time.sleep(0.1)

            headers = { "Range": "bytes="+str(start)+"-"+str(end) }

            self.parts = self.get_downloaded_parts() or []
            part_name = str(f"{i+1:05d}")
            if part_name in self.parts: self.downloaded_parts += 1; continue

            t = threading.Thread(target=self.download_part, args=(headers, i+1, self.thread_number))
            self.threads.append(self.thread_number)
            self.thread_number += 1
            t.start()

        while len(self.threads) > 0:
            time.sleep(0.1)

        files = [f for f in glob.glob(f"{self.temp_folder}\\{self.hash}\\*")]
        files.sort()

        with open(f"{self.temp_folder}\\{self.hash}\\{self.filename_all}", "ab") as f:
            for file in files:
                file = open(file, "rb").read()
                f.write(file)

        shutil.move(f"{self.temp_folder}\\{self.hash}\\{self.filename_all}", f"{self.save_path}\\{self.filename_all}")
        shutil.rmtree(f"{self.temp_folder}\\{self.hash}")
        self.end_time = time.time()

        self.output(f"{colorama.Fore.CYAN}============================")
        self.output(f"{colorama.Fore.CYAN}Downloaded {self.filename_all}")
        self.output(f"{colorama.Fore.CYAN}Size {self.file_size_clean} | {self.file_size} bytes")
        self.output(f"{colorama.Fore.CYAN}Time Taken: {math.floor(self.end_time - self.start_time)} seconds")
        self.output(f"{colorama.Fore.CYAN}Location: {self.save_path}\\{self.filename_all}")
        self.output(f"{colorama.Fore.CYAN}============================")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--url', '-u', required=False, type=str, help='direct url to the file/video/etc. i.e. "https://www.youtube.com/video.mp4"')
    parser.add_argument('--filename', '-f', required=False, type=str, help='name of the file including the extention. i.e. "video.mp4"')
    parser.add_argument('--save_path', '-o', required=False, type=str, help='download path. i.e. "C:/users/user/downloads" (default is where dlf.py is located)')
    parser.add_argument('--chunk_size', '-cs', required=False, type=float, help='size of chunks to download. i.e. 0.5 (chunk size * 1MB) (default is 0.5MB)')
    parser.add_argument('--concurrent_downloads', '-c', required=False, type=int, help='concurrent downloads. (default is 20)')
    parser.add_argument('--show_info', '-v', required=False, action='store_true', help='show debug info.')
    parser.add_argument('--uid', '-uid', required=False, action='store_true')
    parser.add_argument('--clean', '-cl', required=False, action='store_true', help='overwrites old download attempts')

    parser.parse_args()
    args = parser.parse_args()

    url = args.url
    filename = args.filename or ".".join(url.split("/")[-1].split(".")[:-1])
    save_path = args.save_path or f"{sys.path[0]}\\dlf"
    chunk_size = args.chunk_size or 0.5
    concurrent_downloads = args.concurrent_downloads or 20
    show_info = args.show_info or False
    clean = args.clean or False

    if args.uid: filename = str(uuid.uuid4()).replace("-", "").lower()
    
    DownloadFile(url, chunk_size, concurrent_downloads, filename, save_path, show_info, clean)


if __name__ == "__main__":
    main()