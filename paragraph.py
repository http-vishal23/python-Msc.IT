para = input("Enter a paragraph: ")

words = para.split()

print("Total words:", len(words))

unique = []
for word in words:
    if word not in unique:
        unique.append(word)

print("Unique words:", len(unique))

longest = words[0]
for word in words:
    if len(word) > len(longest):
        longest = word
print("Longest word:", longest)

shortest = words[0]
for word in words:
    if len(word) < len(shortest):
        shortest = word
print("Shortest word:", shortest)

print("Repeated words:")
for word in unique:
    if words.count(word) > 1:
        print(word)
