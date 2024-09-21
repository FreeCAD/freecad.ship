# About translating Ship Workbench

<!--toc:start-->
- [About translating Ship Workbench](#about-translating-ship-workbench)
  - [Updating translations template file](#updating-translations-template-file)
  - [Creating file for missing locale](#creating-file-for-missing-locale)
    - [Using script](#using-script)
    - [Renaming file](#renaming-file)
  - [Translating](#translating)
  - [Compiling translations](#compiling-translations)
  - [Sending translations](#sending-translations)
  - [More information](#more-information)
<!--toc:end-->

> [!NOTE]
> All commands **must** be run in `./freecad/ship/resources/translations/` directory.

> [!IMPORTANT]
> If you want to update/release the files you need to have installed
> `lupdate` and `lrelease` from Qt6 version. Using the versions from
> Qt5 is not advised because they're buggy.

## Updating translations template file

To update the template file from source files you should use this command:

```shell
./update_translation.sh -U
```

Once done you can commit the changes and upload the new file to CrowdIn platform
at <https://crowdin.com/project/freecad-addons> webpage and find the **Ship** project.

## Creating file for missing locale

### Using script

To create a file for a new language with all **Ship** translatable strings execute
the script with `-u` flag plus your locale:

```shell
./update_translation.sh -u es-ES
```

### Renaming file

Also you can rename new `Ship.ts` file by appending the locale code,
for example, `Ship_es-ES.ts` for Spanish (Spain) and change

```xml
<TS version="2.1">
```

to

```xml
<TS version="2.1" language="es_ES" sourcelanguage="en">
```

As of 13/09/2024 the supported locales on FreeCAD
(according to `FreeCADGui.supportedLocales()`) are 43:

```python
{'English': 'en', 'Afrikaans': 'af', 'Arabic': 'ar', 'Basque': 'eu',
'Belarusian': 'be', 'Bulgarian': 'bg', 'Catalan': 'ca',
'Chinese Simplified': 'zh-CN', 'Chinese Traditional': 'zh-TW', 'Croatian': 'hr',
'Czech': 'cs', 'Dutch': 'nl', 'Filipino': 'fil', 'Finnish': 'fi', 'French': 'fr',
'Galician': 'gl', 'Georgian': 'ka', 'German': 'de', 'Greek': 'el', 'Hungarian': 'hu',
'Indonesian': 'id', 'Italian': 'it', 'Japanese': 'ja', 'Kabyle': 'kab',
'Korean': 'ko', 'Lithuanian': 'lt', 'Norwegian': 'no', 'Polish': 'pl',
'Portuguese': 'pt-PT', 'Portuguese, Brazilian': 'pt-BR', 'Romanian': 'ro',
'Russian': 'ru', 'Serbian': 'sr', 'Serbian, Latin': 'sr-CS', 'Slovak': 'sk',
'Slovenian': 'sl', 'Spanish': 'es-ES', 'Spanish, Argentina': 'es-AR',
'Swedish': 'sv-SE', 'Turkish': 'tr', 'Ukrainian': 'uk', 'Valencian': 'val-ES',
'Vietnamese': 'vi'}
```

## Translating

To edit your language file open your file in `Qt Linguist` from `qt5-tools`/`qt6-tools`
package or in a text editor like `xed`, `mousepad`, `gedit`, `nano`, `vim`/`nvim`,
`geany` etc. and translate it.

Alternatively you can visit the **FreeCAD-addons** project on CrowdIn platform
at <https://crowdin.com/project/freecad-addons> webpage and find your language,
once done, look for the **Ship** project.

## Compiling translations

To convert all `.ts` files to `.qm` files (merge) you can use this command:

```shell
./update_translation.sh -R
```

If you are a translator that wants to update only their language file
to test it on **FreeCAD** before doing a PR you can use this command:

```shell
./update_translation.sh -r es-ES
```

This will update the `.qm` file for your language (Spanish (Spain) in this case).

## Sending translations

Now you can contribute your translated `.ts` file to **Ship** repository,
also include the `.qm` file.

<https://github.com/FreeCAD/freecad.ship>

## More information

You can read more about translating external workbenches here:

<https://wiki.freecad.org/Translating_an_external_workbench>
