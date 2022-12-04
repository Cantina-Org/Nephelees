> Liste nom de projet
>1. **Cantina**
>2. Toxicity
>3. Born


>## Schema de la base de donnée
>>### Table Instance 
>>> Colone n°1<br>
>>> Nom: ID<br>
>>> Type: INT<br>
>>> Autoincrement: True<br>
>>
>>> Colone n°2<br>
>>> Nom: Token<br>
>>> Type: TEXT
>>
>>> Colone n°3<br>
>>> Nom: nom_instance<br>
>>> Type: TEXT
>>
>>> Colone n°4<br>
>>> Nom: ip<br>
>>> Type: TEXT<br>
>>
>>> Colone n°5<br>
>>> Nom: official<br>
>>> Type: BOOL<br>
>>
>>> Colone n°6<br>
>>> Nom: private<br>
>>> Type: BOOL<br>
>>
>>> Colone n°7<br>
>>> Nom: usefull_data<br>
>>> Type: BOOL<br>
>>
>>> Colone n°8<br>
>>> Nom: owner_id<br>
>>> Type: INT? TEXT?<br>
>>
>>> Colone n°9<br>
>>> Nom: moderator_id<br>
>>> Type: INT? TEXT?<br>
>>
>>> Colone n°10<br>
>>> Nom: user_id<br>
>>> Type: INT? TEXT?<br>
>>
>>> Colone n°11<br>
>>> Nom: online<br>
>>> Type: BOOL<br>
>>
>>> Colone n°12<br>
>>> Nom: last_online<br>
>>> Type: BOOL<br>
>>
>>> Colone n°13<br>
>>> Nom: warn_level<br>
>>> Type: INT<br>
> 
> `CREATE IF NOT EXISTS TABLE instance(ID INT PRIMARY KEY NOT NULL AUTO_INCREMENT, token TEXT, nom_instance TEXT, ip TEXT, official BOOL, private BOOL, usefull_data BOOL, owner_id INT, moderator_id TEXT, user_id TEXT, online BOOL, last_online TEXT, warn_level INT)`