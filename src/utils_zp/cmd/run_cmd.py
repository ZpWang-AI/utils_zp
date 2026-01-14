from ..base import *


def run_cmd(
    cmd: List[str], 
    log_filepath: Optional[str] = None, 
    env_dict: Optional[Dict[str, str]] = None,
) -> bool:
    env = os.environ.copy()
    if env_dict:
        env.update(env_dict)
    
    print('>', ' '.join(cmd))
    
    if log_filepath is None:
        # No log file case
        result = subprocess.run(
            cmd,
            env=env,
            check=True,
            text=True,
            encoding=utf8,
            capture_output=False  # Let output go directly to terminal
        )
        print(f'\n> Done!')
        return True
    
    else:
        print(f"> log file: {log_filepath}")

        output_lock = threading.Lock()

        def read_output(pipe, file_handle, is_stderr=False):
            try:
                with pipe:
                    for line in iter(pipe.readline, ''):
                        if line:
                            with output_lock:
                                file_handle.write(line)
                                file_handle.flush()
                            
                            if is_stderr:
                                # sys.stderr.write(f"\033[91m{line}\033[0m")
                                sys.stderr.write(line)
                            else:
                                sys.stdout.write(line)
            except Exception as e:
                print(f"Error reading output: {e}")
        
        with open(log_filepath, "w", encoding=utf8) as log_file:
            log_file.write(gap_line("Command Start")+endl*2)
            log_file.flush()
            
            result = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding=utf8,
                bufsize=1,  # 行缓冲
                universal_newlines=True
            )
            
            stdout_thread = threading.Thread(
                target=read_output, 
                args=(result.stdout, log_file, False),
                # daemon=True,
            )
            stderr_thread = threading.Thread(
                target=read_output, 
                args=(result.stderr, log_file, True),
                # daemon=True,
            )
            
            stdout_thread.start()
            stderr_thread.start()
            result.wait()
            stdout_thread.join()
            stderr_thread.join()
            
            log_file.write(endl+gap_line("Command End")+endl)
            log_file.write(f"\nReturn code: {result.returncode}\n")

        # 检查返回码
        if result.returncode != 0:
            print(f"\n> Fail! return code: {result.returncode}")
            return False
        else:
            print(f'\n> Done!')
            return True



