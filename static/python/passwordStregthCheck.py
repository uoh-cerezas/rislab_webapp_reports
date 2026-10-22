import string

def passwordStrengthTest(password):
    length = len(password)

    upper_case = any([1 if c in string.ascii_uppercase else 0 for c in password])
    lower_case = any([1 if c in string.ascii_lowercase else 0 for c in password])
    special_chars = any([1 if c in string.punctuation else 0 for c in password])
    digits = any([1 if c in string.digits else 0 for c in password])

    character_types = [upper_case, lower_case, special_chars, digits]

    if length > 9 and sum(character_types) > 3:
        # print("Su contrasena es fuerte, bien hecho.")
        return True
    elif length <= 9 or sum(character_types) <= 3:
        # print("Su contrasena es debil, debe incluir al menos una mayuscula, una minúscula, un número y un carácter especial.")
        return False