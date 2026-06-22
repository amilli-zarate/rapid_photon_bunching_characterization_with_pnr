from pathlib import Path

def interact(message_filename, valid_options=False, restrictions=False):

    with open(Path('messages')/message_filename, 'r') as message:

        for line in message:
            print(line, end="", flush=True)
        
    command = input()

    if valid_options != False:
        while command not in valid_options:
            print("Choose a valid option", flush=True)
            command = input()

    if restrictions != False:
        compliance = False
        while not compliance:
            for i,restriction in enumerate(restrictions,1):
                compliance = restriction(command)
                if not compliance:
                    print(f"Restriction {i} is not met. Try again :")
                    command = input()
                    continue

    return command


def parallelization_query():

    parallel_choice = interact('optional_parallel_config', ('y','n'))

    if parallel_choice == 'y':
        num_params_per_thread = eval(
            interact('choose_parallel_config',
            restrictions=(
                lambda command:isinstance( eval(command), list) ,
                lambda command:sum(eval(command))==4155
                )
            )
        )
    elif parallel_choice == 'n':
        num_params_per_thread = [4155]*1

    return num_params_per_thread