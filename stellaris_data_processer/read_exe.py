import re

base_exe = r'L:\python_working_dir\stellaris\ori\stellaris.exe'
out_file = r'L:\python_working_dir\stellaris\ori\stellaris.txt'


def progress(iterator, record, all_length):
    if (iterator * 20) / all_length > record:
        print('Processed: ' + str(record * 5) + '%.')
        record += 1
    return record


if __name__ == '__main__':
    new_array = []
    with open(base_exe, 'rb') as f:
        all_str = f.read()
    print('Read done.')
    print('Recode:')
    j = 1
    for i in range(len(all_str)):
        j = progress(i, j, len(all_str))
        byte = all_str[i]
        if byte < 0x20 or byte > 0x7e:
            new_array.append(0x0A)
        else:
            new_array.append(byte)
    print('Recode done.')
    new_bytes = bytes(new_array)
    new_str = new_bytes.decode(encoding='utf-8')
    new_list =new_str.split('\n')
    print('Split done, length: ' + str(len(new_list)))
    refined_list = []
    data_segment = False
    print('Find data:')
    j = 1
    for i in range(len(new_list)):
        j = progress(i, j, len(new_list))
        if i != 0 and i != len(new_list) -1:
            if len(new_list[i]) >= 3:
                refined_list.append(new_list[i])
                data_segment = True
            elif len(new_list[i]) > 0:
                if len(new_list[i - 1]) > 3 or len(new_list[i + 1]) > 3:
                    refined_list.append(new_list[i])
                elif data_segment:
                    refined_list.append(new_list[i])
            else:
                data_segment = False
    print('Find data done.')
    refined = ''
    print('Reorganised:')
    j = 1
    for i in range(len(refined_list)):
        j = progress(i, j, len(refined_list))
        refined = refined + refined_list[i] + '\n'
    print('Reorganised done.')
    with open(out_file, 'w', encoding='utf-8') as f:
        f.write(refined)
    print('Output done.')
    z = 1
