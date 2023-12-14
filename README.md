# brBug

`brBug` is a tool/library to debug android BeeWare apps on Android with ease.

## Installation
Install using pip: `pip install brbug`.
```bash
pip install brbug
```
If you want the `rich` version of the `brbug` CLI, you can also install it using: `pip install brbug[rich]`

If you manage your briefcase dependencies using `pyproject.toml`, add `brdebug` to the app `requires`.

## Usage

brBug contains two part: the toga part and the build part.

At the build instead of running your android app with:

```bash
briefcase run android -u -d device_id
```

you can run it with:

```bash
brbug -d device_id
```

(or if you want you can also disable the `briefcase run` command using `-X`, and just stay with the build step like this `brbug -X -d device_id && briefcase run ...`).

After you can see that in you `resources` folder there is a file called `_brbug.tar.gz`. 

Then in your toga app use it like this:

```python
import brbug
@brbug.catch_beeapp
class YourTogaApp(toga.App):
```

That's it.
Now `brbug` will use the `.tar.gz` file to create better traceback (using [friendly-traceback](https://friendly-traceback.github.io/docs/index.html)).

Here is an example of better traceback with brBug :

```python
W/python.stderr: Traceback (most recent call last):
W/python.stderr:   File "/data/data/com.matan_h.ipython.bee_ipython/files/chaquopy/AssetFinder/requirements/brbug/brbug.py", line 146, in wrapper
W/python.stderr:     
W/python.stderr:   File "/data/data/com.matan_h.ipython.bee_ipython/files/chaquopy/AssetFinder/app/bee_ipython/app.py", line 38, in startup
W/python.stderr:     nameerror
W/python.stderr: NameError: name 'nameerror' is not defined. Did you mean: 'NameError'?
W/python.stderr: 
W/python.stderr: A `NameError` exception indicates that a variable or
W/python.stderr: function name is not known to Python.
W/python.stderr: Most often, this is because there is a spelling mistake.
W/python.stderr: However, sometimes it is because the name is used
W/python.stderr: before being defined or given a value.
W/python.stderr: Did you mean `NameError`?
W/python.stderr: In your program, no object with the name `nameerror` exists.
W/python.stderr: The Python builtin `NameError` has a similar name.
W/python.stderr: 
```

compare this to the default android python crash/traceback:

```python
E/AndroidRuntime: Caused by: com.chaquo.python.PyException: NameError: name 'nameerror' is not defined
E/AndroidRuntime:   at <python>.bee_ipython.app.startup(app.py:38)
E/AndroidRuntime:   at <python>.toga.app._startup(app.py:624)
E/AndroidRuntime:   at <python>.toga_android.app.create(app.py:179)
E/AndroidRuntime:   at <python>.toga_android.app.main_loop(app.py:199)
E/AndroidRuntime:   at <python>.toga.app.main_loop(app.py:663)
E/AndroidRuntime:   at <python>.__main__.<module>(__main__.py:3)
E/AndroidRuntime:   at <python>.runpy._run_code(<frozen runpy>:88)
```

## Supported tools

brBug modifies the `executing` engine to work on android using the `tar.gz` source. 

That mean, by extension it supports most debugging tools:

* [snoop](https://github.com/alexmojaki/snoop) - if you don't know this yet, highly recommended - it's awesome.
* [python-devtools](https://github.com/samuelcolvin/python-devtools). 
* friendly-traceback - this package already provide it by default.
* [icecream](https://github.com/gruns/icecream) (although it doesn't look good in the android logcat view - somehow each word is in different line)

## How its works

Chaquopy/beeware python apps are in a `pyc` state, which mean that no line information is stored.
 That cause the normal python traceback/error to look like this:

The `build` side generate `.tar.gz` file of all `.py` files in your application directory, then the `toga` side open it, find the python source and modify `executing` to use it as source. 

#### Why I need this `@brbug.catch_beeapp` ? It cannot just catch the errors automatically?

The "normal" way to catch errors is to use `sys.excepthook`. Unfortunately [chaquopy doesn't support it](https://github.com/chaquo/chaquopy/issues/1053). The other way is use `try/except`. But then `executing` came across `app.mainloop` it crashes, as It's pretty much a java method (`executing.executing.NotOneValueFound`). Maybe in the future I will create a `mrbug.automatic` module which detect and catch the toga app automatically. 
### what `@brbug.catch_beeapp` does?
It wraps every method you defined (And not the ones that are inherited) with `try/ except : print traceback` to make it able to print traceback when a function fails

## FAQ
### What not supported

* `rich.traceback` - it uses the traceback object instead of `executing` or `stack_data`, so I cannot support it. 

### How to report errors/problems/suggestions

please open a [GitHub issue](https://github.com/matan-h/brbug/issues)

### Why it's named 'brBug'

It's like `briefcaseBug` but no one can spell it right, so `brBug`. 
it also sounds like `mr. Bug` which is nice.

### How can I donate you

If you found this tool/library useful, it would be great if you could buy me a coffee:

<a href="https://www.buymeacoffee.com/matanh" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-blue.png" alt="Buy Me A Coffee" height="47" width="200"></a>