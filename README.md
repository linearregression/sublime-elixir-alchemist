[![License GPL 3](https://img.shields.io/badge/license-GPL_3-green.svg)](http://www.gnu.org/licenses/gpl-3.0.txt)

# Sublime Elixir Alchemist
## What is this?
sublime-elixir-alchemist is a sublime text plugin that attempts to provide all of the functionality of the emacs alchemist plugin to [SublimeText 3](http://www.sublimetext.com/3).  It does this by using the actual [alchemist-server](https://github.com/tonini/alchemist-server) under the hood to provide all of the functionality.  Send all of your money to [Samuel Tonini](https://github.com/tonini).  He deserves it.

## Why would you do this?
The current options for sublime text don't handle autocomplete for macros or my imported libraries, which is a bummer.  [Emacs](https://www.gnu.org/software/emacs/) does via alchemist, but emacs is a bummer (sorry emacs fans).  [Spacemacs](https://github.com/syl20bnr/spacemacs) and Emacs in [evil mode](http://www.emacswiki.org/emacs/Evil) are cool, but they're not as fast as Sublime.  Why not [Atom](https://atom.io/)?  It's pokey, and I am better with python than I am with Javascript.  If I manage to get all of this working, I might build one for atom as well.

## Does it work yet?
It does on my box!  It is currently in development.  I haven't set it up to work with anything other than my laptop.  If you check it out in your _Sublime Text 3 Packages_ folder right now, it might work.  It also might not.  If it doesn't it's because I haven't built it to be portable yet.  I'm working on getting it working for everything, and I'll update this when I do.  Until it's available on package control, don't open any bugs.

## What does work on your box?
Code completion works.  The definition lookup of code will open the file, but it doesn't focus the screen on the method or module yet.  I'm getting to that as well.  I bound mine to super-r, but I'll make that configurable as well.  Let me know if you have any questions.

# Alchemist Server
The Alchemist-Server operates as an informant for a specific desired
Elixir Mix project and serves the following data.  Anything checked has been at least partially implemented:
- [x] Completion for Modules and functions.
- [ ] Documentation lookup for Modules and functions.
- [ ] Code evaluation and quoted representation of code.
- [x] Definition lookup of code.
- [ ] Listing of all available Mix tasks.
- [ ] Listing of all available Modules with documentation.

**INFO:** The Alchemist-Server that makes this work is in Beta status and the API will most likely change until the first release.
