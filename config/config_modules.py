import os, sys
from config import sdlconfig, pkgconfig, helpers
from config import config_msys, config_unix, config_win, config_darwin
from config.config_generic import Dependency

OS_MODULES = {
    'win'   : config_win,
    'msys'  : config_msys,
    'unix'  : config_unix,
    'darwin': config_darwin
}

def get_dependencies(buildsystem, cfg):
    """
        Returns a dict with all the configured libraries which 
        will be used when linking PyGame modules.

        Configuring a library implies finding its location
        and storing the compiler/linker arguments which
        will be passed to all the modules which rely on such
        library.
    """
    dep = OS_MODULES[buildsystem].Dependency
    pygame_sdl_path = os.path.join ("src", "sdl")

    DEPENDENCIES = {
        'sdl' : dep(
            'SDL.h', 'SDL',
            config_program='sdl-config',
            pkgconfig_name='sdl',
            extra_include_dirs = [pygame_sdl_path]),

        'sdl_mixer' : dep(
            'SDL_mixer.h', 'SDL_mixer',
            config_program='sdl-config',
            pkgconfig_name='sdl',
            extra_include_dirs = [pygame_sdl_path]),

        'sdl_ttf' : dep(
            'SDL_ttf.h', 'SDL_ttf',
            config_program='sdl-config',
            pkgconfig_name='sdl',
            extra_include_dirs = [pygame_sdl_path]),

        'sdl_gfx' : dep(
            'SDL_framerate.h', 'SDL_gfx',
            config_program='sdl-config',
            pkgconfig_name='sdl',
            extra_include_dirs = [pygame_sdl_path]),

        'sdl_image' : dep(
            'SDL_image.h', 'SDL_image',
            config_program='sdl-config',
            pkgconfig_name='sdl',
            extra_include_dirs = [pygame_sdl_path]),

        'png' : dep(
            'png.h', 'png',
            pkgconfig_name='libpng'),

        'jpeg' : dep(
            'jpeglib.h', 'jpeg',
            pkgconfig_name='libjpeg'),

        'freetype' : dep(
            'freetype.h', 'freetype',
            pkgconfig_name='freetype2',
            config_program='freetype-config'),
    }

    for (dep_name, dep) in DEPENDENCIES.items():
        dep.configure(cfg)

    return DEPENDENCIES

def sdl_get_version(buildsystem):
    """
        Returns the version of the installed SDL library
    """
    return OS_MODULES[buildsystem].sdl_get_version()

def get_sys_libs(buildsystem, module):
    """
        Return a list with any system-specific libraries
        which must be linked together with a module
    """
    return OS_MODULES[buildsystem].get_sys_libs(module)

def get_install_libs(buildsystem, cfg):
    """
        Return a list with the libraries which must be bundled
        and installed with Pygame, based on the active OS
    """
    return OS_MODULES[buildsystem].get_install_libs(cfg)

def prepare_modules(buildsystem, modules, cfg):
    """
        Updates all the modules that must be built by adding
        compiler/link information for the libraries on which
        they depend.

        buildsystem - The active build system
        modules - List of module.Module objects
        cfg - The currently loaded 'cfg' module
    """

    os_config = OS_MODULES[buildsystem]

    # configure our library dependencies
    dependencies = get_dependencies(buildsystem, cfg)

    for mod in modules:
        mod.canbuild = True

        # add build/link information for the library dependencies 
        # on which mod relies.
        # if one of the required libraries cannot be found,
        # the module will be disabled (cannot be built)
        for dep_name in mod.depends:
            dep_name = dep_name.lower()

            if dep_name not in dependencies:
                raise Exception("Invalid library dependency: '%s'" % dep_name)

            dep = dependencies[dep_name]
            dep.setup_module(mod, False)

        # add build/link information for optional libraries
        # our module might rely on.
        # if one of the optional libraries cannot be found,
        # nothing bad happens. The module will be built but may
        # lack some of its functionality
        for dep_name in mod.optional_dep:
            dep_name = dep_name.lower()

            if dep_name in dependencies:
                dep = dependencies[dep_name]
                dep.setup_module(mod, True)

        # add any OS-specific libraries
        mod.libs += os_config.get_sys_libs(mod.name) or []