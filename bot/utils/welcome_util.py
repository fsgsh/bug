def get_default_welcome(chat, user):
    if chat.id == 1374518507:  # Aurora Droid
        return f"""
        \n**Hey** [{user.first_name}](tg://user?id={user.id}) `{user.id}`
        \n**Welcome to** {chat.title}
        \n**How are you?**
        \n** • Tap confirm button to join, else auto-removed.**
        \n** • Kindly read pinned post for latest updates. **
        \n** • Use** #faq **for FAQ's &** /notes *for any help. **
        """
    if chat.id == 1361570927:  # Aurora Store
        return f"""
        \n**Hey** [{user.first_name}](tg://user?id={user.id}) `{user.id}`
        \n**Welcome to** {chat.title}
        \n**How are you?**
        \n** • Tap confirm button to join, else auto-removed.**
        \n** • Kindly read pinned post for latest updates. **
        \n** • Use** #faq **for FAQ's &** /notes **for any help. **
        """
    else:  # Other chats
        return f"""
        \n**Hey** [{user.first_name}](tg://user?id={user.id}) `{user.id}`
        \n**Welcome to** {chat.title}
        \n**How are you?**
        \n** • Tap confirm button to join, else auto-removed.**
        """
