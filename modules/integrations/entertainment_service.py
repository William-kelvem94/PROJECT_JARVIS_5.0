"""
Entertainment Features
Jokes, fun facts, and entertainment capabilities
"""

import random
from typing import Optional, List, Dict
import requests


class JokeService:
    """
    Joke and entertainment service.
    
    Features:
    - Random jokes
    - Multiple joke categories
    - Dad jokes
    - Programming jokes
    """
    
    def __init__(self):
        """Initialize joke service."""
        self.joke_api_url = "https://official-joke-api.appspot.com/jokes/random"
        self.dad_joke_api_url = "https://icanhazdadjoke.com/"
        
        # Fallback jokes in Portuguese
        self.fallback_jokes_pt = [
            "Por que o programador foi preso? Porque ele matou o processo!",
            "O que um arquivo disse para o outro? Não me compacte!",
            "Por que o computador foi ao médico? Porque ele estava com vírus!",
            "O que é um terapeuta? É um arquivo de 1024 gigapeutas!",
            "Por que o Python é tão legal? Porque ele não tem ponto e vírgula!",
            "O que o Java disse para o C? Você não tem classe!",
            "Por que os programadores preferem dark mode? Porque a luz atrai bugs!",
            "O que acontece quando você cruza um computador com um elefante? Muita memória!",
            "Por que o desenvolvedor saiu do banho? Porque acabou o shampoo de dados!",
            "Como você chama um programador que não gosta de pessoas? Anti-social network!"
        ]
        
        self.programming_jokes = [
            "There are only 10 types of people: those who understand binary and those who don't.",
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "A SQL query walks into a bar, sees two tables and asks: 'Can I join you?'",
            "How many programmers does it take to change a light bulb? None, it's a hardware problem!",
            "Why did the programmer quit? Because they didn't get arrays!",
            "What's a programmer's favorite hangout place? Foo Bar!",
            "Why do Java developers wear glasses? Because they can't C#!",
            "I would tell you a UDP joke, but you might not get it.",
            "A programmer's wife tells him: 'Go to the store and buy a carton of milk, and if they have eggs, get a dozen.' He comes back with 12 cartons of milk.",
            "Why did the developer go broke? Because he used up all his cache!"
        ]
        
        print("[Jokes] ✓ Entertainment service initialized")
    
    def get_random_joke(self, language: str = 'pt') -> str:
        """
        Get a random joke.
        
        Args:
            language: Language preference ('pt' or 'en')
            
        Returns:
            Joke string
        """
        if language == 'pt':
            return random.choice(self.fallback_jokes_pt)
        else:
            # Try to get from API
            try:
                response = requests.get(self.joke_api_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    setup = data.get('setup', '')
                    punchline = data.get('punchline', '')
                    return f"{setup} {punchline}"
            except:
                pass
            
            # Fallback to programming jokes
            return random.choice(self.programming_jokes)
    
    def get_dad_joke(self) -> str:
        """
        Get a dad joke.
        
        Returns:
            Dad joke string
        """
        try:
            headers = {'Accept': 'application/json'}
            response = requests.get(self.dad_joke_api_url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('joke', self.get_random_joke('en'))
        except:
            pass
        
        return self.get_random_joke('en')
    
    def get_programming_joke(self) -> str:
        """Get a programming-related joke."""
        return random.choice(self.programming_jokes)
    
    def get_joke_by_type(self, joke_type: str = 'random') -> str:
        """
        Get joke by type.
        
        Args:
            joke_type: Type of joke ('random', 'dad', 'programming', 'pt')
            
        Returns:
            Joke string
        """
        if joke_type == 'dad':
            return self.get_dad_joke()
        elif joke_type == 'programming':
            return self.get_programming_joke()
        elif joke_type == 'pt':
            return random.choice(self.fallback_jokes_pt)
        else:
            return self.get_random_joke()


class FunFactsService:
    """
    Fun facts and interesting information service.
    """
    
    def __init__(self):
        """Initialize fun facts service."""
        self.facts_pt = [
            "O Python foi nomeado em homenagem ao grupo de comédia britânico Monty Python!",
            "O primeiro bug de computador foi uma mariposa real encontrada em um computador em 1947!",
            "A senha mais comum do mundo é '123456'.",
            "Google processa mais de 8.5 bilhões de buscas por dia!",
            "O primeiro domínio registrado na internet foi Symbolics.com em 1985.",
            "O email existe desde 1971, antes mesmo da World Wide Web!",
            "A linguagem C foi criada em 1972 por Dennis Ritchie.",
            "O Linux foi criado por Linus Torvalds em 1991 quando ele tinha apenas 21 anos!",
            "O WiFi não significa 'Wireless Fidelity', é apenas um nome comercial!",
            "O primeiro computador pessoal foi o Altair 8800, lançado em 1975."
        ]
        
        print("[FunFacts] ✓ Fun facts service initialized")
    
    def get_random_fact(self) -> str:
        """Get a random fun fact."""
        return random.choice(self.facts_pt)
    
    def get_tech_fact(self) -> str:
        """Get a technology-related fun fact."""
        return random.choice(self.facts_pt)


class QuoteService:
    """
    Inspirational quotes service.
    """
    
    def __init__(self):
        """Initialize quotes service."""
        self.quotes = [
            "O único modo de fazer um ótimo trabalho é amar o que você faz. - Steve Jobs",
            "A inovação distingue um líder de um seguidor. - Steve Jobs",
            "Simplicidade é a máxima sofisticação. - Leonardo da Vinci",
            "O computador nasceu para resolver problemas que não existiam antes. - Bill Gates",
            "Qualquer tecnologia suficientemente avançada é indistinguível de magia. - Arthur C. Clarke",
            "O futuro pertence àqueles que acreditam na beleza de seus sonhos. - Eleanor Roosevelt",
            "Programe como se a pessoa que manterá seu código fosse um psicopata violento que sabe onde você mora. - John Woods",
            "Primeiro, resolva o problema. Depois, escreva o código. - John Johnson",
            "Código é como humor. Quando você tem que explicá-lo, é ruim. - Cory House",
            "A melhor maneira de prever o futuro é inventá-lo. - Alan Kay"
        ]
        
        print("[Quotes] ✓ Quote service initialized")
    
    def get_random_quote(self) -> str:
        """Get a random inspirational quote."""
        return random.choice(self.quotes)
    
    def get_tech_quote(self) -> str:
        """Get a technology-related quote."""
        return random.choice(self.quotes)


# Example usage
if __name__ == "__main__":
    # Jokes
    print("\n=== Jokes ===")
    jokes = JokeService()
    print(f"Random PT: {jokes.get_random_joke('pt')}")
    print(f"Random EN: {jokes.get_random_joke('en')}")
    print(f"Dad joke: {jokes.get_dad_joke()}")
    print(f"Programming: {jokes.get_programming_joke()}")
    
    # Fun facts
    print("\n=== Fun Facts ===")
    facts = FunFactsService()
    print(f"Fact: {facts.get_random_fact()}")
    
    # Quotes
    print("\n=== Quotes ===")
    quotes = QuoteService()
    print(f"Quote: {quotes.get_random_quote()}")
