from discord.ext.commands import Bot
from discord.ext import commands
from discord_slash import SlashContext
from lib.util import command_decorator, subcommand_decorator
from dataclasses import dataclass
import epicbox


@dataclass
class Language:
    file: str
    language: str
    image: str
    command: str

    def run(self, code):
        limits = {
            # CPU time in seconds, None for unlimited
            'cputime': 60,
            # Real time in seconds, None for unlimited
            'realtime': 120,
            # Memory in megabytes, None for unlimited
            'memory': 64,

            # limit the max processes the sandbox can have
            # -1 or None for unlimited(default)
            'processes': -1,
        }
        files = [{'name': self.file, 'content': code.encode('utf-8')}]
        return epicbox.run(self.language, self.command,
                           files=files, limits=limits)


languages = [
    Language('main.py', 'python',
             'python:latest', 'python3 main.py'),
    Language('main.c', 'c', 'gcc:latest',
             'gcc main.c -o main && ./main'),
    Language('Main.hs', 'haskell', 'haskell:latest',
             'ghc Main.hs && ./Main'),
    Language('main.bf', 'brainfuck',
             'esolang/brainfuck-esotope:latest', 'brainfuck-esotope main.bf'),
    Language('Main.java', 'java', 'openjdk:15',
             'javac Main.java && java Main'),
    Language('main.rs', 'rust', 'rust:latest',
             'rustc main.rs && ./main'),
    Language('main.cpp', 'cpp', 'gcc:latest',
             'g++ main.cpp -o main && ./main'),
    Language('main.cs', 'c#', 'mono:latest',
             'mcs -out:main.exe main.cs && mono main.exe'),
    Language('main.go', 'golang', 'golang:latest', 'go run main.go'),
    Language('main.js', 'js', 'node:latest', 'node main.js'),
    Language('main.ts', 'ts', 'zachdeibert/typescript:latest',
             'tsc main.ts && node main.js'),
    Language('main.dart', 'dart',
             'google/dart:latest', 'dart main.dart'),
    Language('main.swift', 'swift', 'swift:latest',
             'swiftc -o main main.swift && ./main'),
    Language('main.clj', 'clojure', 'clojure:latest', 'clj main.clj'),
    Language('main.lua', 'lua',
             'woahbase/alpine-lua:latest', 'lua main.lua'),
    Language('main.ml', 'ocaml', 'ocaml/opam2:latest',
             'ocamlc -o main main.ml && ./main'),
    Language('main.php', 'php', 'php:latest',
             'php main.php'),
    Language('main.r', 'r', 'r-base:latest',
             'Rscript main.r'),
    Language('main.rb', 'ruby', 'ruby:latest', 'ruby main.rb'),
    Language('main.fsx', 'fsharp',
             'fsharp:latest', 'fsharpi main.fsx'),
    Language('main.kt', 'kotlin', 'zenika/kotlin:latest',
             'kotlinc main.kt -include-runtime -d main.jar && java -jar main.jar'),
    Language('main.scala', 'scala',
             'hseeberger/scala-sbt:8u222_1.3.5_2.13.1', 'scala Main.scala'),
    Language('main.sh', 'bash', 'bash:latest', 'bash main.sh'),
    Language('main.lsp', 'lisp', 'daewok/lisp-devel:latest',
             'sbcl --script main.lsp'),

]


class Sandbox(commands.Cog):
    """Describe what the cog does."""

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        epicbox.configure(
            profiles=[
                epicbox.Profile(l.language, l.image) for l in languages
            ]
        )

    @command_decorator(lang={'description': 'Language to execute last block in', "choices": [l.language for l in languages]})
    async def exec(self, ctx: SlashContext, lang: str) -> None:
        """Execute your last code block message

        """
        await ctx.defer()
        messages = await ctx.channel.history(limit=100).flatten()
        try:
            last_code_block = [m for m in messages if m.author.id ==
                               ctx.author.id and m.content.startswith('```')][0].content
        except IndexError:
            await ctx.send(":x: You haven't made any code blocks!")
            return
        code = '\n'.join(
            list(filter(lambda x: '```' not in x, last_code_block.split('\n'))))

        lang = next(filter(lambda x: x.language == lang, languages))

        result = lang.run(code)

        if result['timeout']:
            output = ':x: TimeoutError: program runtime exceeded timeout.'
        elif result['oom_killed']:
            output = ':x: MemoryError: program exceeded memory limit'
        else:
            output = f'Exit code: {result["exit_code"]}\n'
            output += f'Duration: {result["duration"]}\n'
            output += f'```\n{result["stdout"].decode("utf-8")}```'

        await ctx.send(output)


def setup(bot: Bot) -> None:
    """Add the extension to the bot."""
    bot.add_cog(Sandbox(bot))
