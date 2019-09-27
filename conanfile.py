#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanInvalidConfiguration
import os


class LibSELinuxConan(ConanFile):
    name = "libselinux"
    version = "2.8"
    description = "Security-enhanced Linux is a patch of the Linux kernel and a number of utilities with enhanced security functionality designed to add mandatory access controls to Linux"
    topics = ("conan", "selinux", "security-enhanced linux")
    url = "https://github.com/bincrafters/conan-libselinux"
    homepage = "https://github.com/SELinuxProject/selinux"
    author = "Bincrafters <bincrafters@gmail.com>"
    license = "Unlicense"  # This library (libselinux) is public domain software, i.e. not copyrighted
    exports = ["LICENSE.md"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}
    _sepol_subfolder = "libsepol-%s" % version
    _selinux_subfolder = "libselinux-%s" % version
    _date = "20180524"
    requires = ("pcre2/10.32",)

    def configure(self):
        del self.settings.compiler.libcxx
        if self.settings.os != "Linux":
            raise ConanInvalidConfiguration("only Linux is supported")

    def build_requirements(self):
        if not tools.which("flex"):
            self.build_requires("flex_installer/2.6.4@bincrafters/stable")

    def source(self):
        source_url = "https://github.com/SELinuxProject/selinux/releases/download/%s/libselinux-%s.tar.gz" % (self._date, self.version)
        tools.get(source_url, sha256="31db96ec7643ce10912b3c3f98506a08a9116dcfe151855fd349c3fda96187e1")
        source_url = "https://github.com/SELinuxProject/selinux/releases/download/%s/libsepol-%s.tar.gz" % (self._date, self.version)
        tools.get(source_url, sha256="3ad6916a8352bef0bad49acc8037a5f5b48c56f94e4cb4e1959ca475fa9d24d6")

    def build(self):
        pcre_inc = os.path.join(self.deps_cpp_info["pcre2"].rootpath,
                                self.deps_cpp_info["pcre2"].includedirs[0])
        pcre_libs = ' '.join(["-l%s" % lib for lib in self.deps_cpp_info["pcre2"].libs])
        sepol_inc = os.path.join(self.source_folder, self._sepol_subfolder, "include")
        with tools.chdir(os.path.join(self._sepol_subfolder, "src")):
            args = ["libsepol.so.1" if self.options.shared else "libsepol.a"]
            env_build = AutoToolsBuildEnvironment(self)
            env_build.make(args=args)
        with tools.chdir(os.path.join(self._selinux_subfolder, "src")):
            args = ["libselinux.so.1" if self.options.shared else "libselinux.a",
                    'PCRE_CFLAGS=-DPCRE2_CODE_UNIT_WIDTH=8 -DUSE_PCRE2=1 -I%s -I%s' % (pcre_inc, sepol_inc),
                    'PCRE_LDLIBS=%s' % pcre_libs]
            env_build = AutoToolsBuildEnvironment(self)
            env_build.make(args=args)

    def package(self):
        self.copy(pattern="LICENSE", dst="licenses", src=self._selinux_subfolder)
        for library in [self._sepol_subfolder, self._selinux_subfolder]:
            self.copy(pattern="*.h", dst="include", src=os.path.join(library, "include"), keep_path=True)
            self.copy(pattern="*.so*", dst="lib", src=library, keep_path=False)
            self.copy(pattern="*.a", dst="lib", src=library, keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["selinux", "sepol"]
