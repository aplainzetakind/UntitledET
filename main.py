import yaml
from classes import drill, drilloptions

def builtin():
    '''This is the built-in drill selection menu. Receives input from the user,
    creates a drill() with the parameters entailed by that input, and runs
    it.'''
    with open('builtin.yaml', 'r') as builtin:
        drills = yaml.load(builtin)

    print('-' * 20 + '\n') 
    print('Please select a drill.\n')

    for i in sorted(drills.keys()):
        print(str(i) + '. ' + drills[i]['name'])
        print('\t' + drills[i]['desc'] + '\n')

    choice = -1

    while not choice in sorted(drills.keys()): 
        choice = int(input('Enter a choice: '))

    options = drilloptions(drills[choice])
    thedrill = drill(options)
    thedrill.run()
    
def customdrill():
    '''The custom drill selector, builder. Does nothing at the moment.'''
    print('\nNot yet implemented.')
    print('-' * 20 + '\n') 
    main()

def main():
    '''The entry point to the program. Simply asks for options.'''
    choice = -1
    sel1 = [1,2]

    while not choice in sel1:
        print('''Please select a category:
        1. Built in drills
        2. Custom drills''')

        choice = input('Enter a choice: ')

    if choice == 1:
        builtin()
    else:
        customdrill()

main()
