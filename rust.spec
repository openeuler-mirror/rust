%global rustlibdir %{_prefix}/lib/rustlib
%global rust_triple %{_target_cpu}-unknown-linux-gnu
%global _privatelibs lib(.*-[[:xdigit:]]{16}*|rustc.*)[.]so.*
%global __provides_exclude ^(%{_privatelibs})$
%global __requires_exclude ^(%{_privatelibs})$
%global __provides_exclude_from ^(%{_docdir}|%{rustlibdir}/src)/.*$
%global __requires_exclude_from ^(%{_docdir}|%{rustlibdir}/src)/.*$
%global _find_debuginfo_opts --keep-section .rustc

Name:           rust
Version:        1.29.1
Release:        3
Summary:        A systems programming language
License:        (ASL 2.0 or MIT) and (BSD and MIT)
URL:            https://www.rust-lang.org
Source0:        https://static.rust-lang.org/dist/rustc-1.29.1-src.tar.xz
Patch0000:      rust-52876-const-endianess.patch
Patch0001:      0001-std-stop-backtracing-when-the-frames-are-full.patch
Patch0002:      0001-Set-more-llvm-function-attributes-for-__rust_try.patch
BuildRequires:  cargo >= 1.28.0 (%{name} >= 1.28.0 with %{name} <= 1.29.1)
BuildRequires:  make gcc-c++ ncurses-devel curl python3 cmake3 >= 3.4.3 procps-ng
BuildRequires:  pkgconfig(libcurl) pkgconfig(liblzma) pkgconfig(openssl) pkgconfig(zlib) gdb
Requires:       %{name}-devel = 1.29.1-%{release}
Provides:       bundled(llvm) = 7.0 bundled(libbacktrace) = 8.1.0 bundled(miniz) = 1.16~beta+r1
Provides:       rustc = 1.29.1-%{release}

%description
Rust is a systems programming language focused on three goals:safety,
speed,and concurrency.It maintains these goals without having a garbage
collector, making it a useful language for a number of use cases other
languages are not good at: embedding in other languages, programs with
specific space and time requirements,and writing low-level code, like
device drivers and operating systems. It improves on current languages
targeting this space by having a number of compile-time safety checks
that produce no runtime overhead,while eliminating all data races.

%package devel
Summary:        Libraries and header files for developing applications that use appstream-glib
Provides:       %{name}-std-static = %{version}-%{release}
Obsoletes:      %{name}-std-static < %{version}-%{release}

%description devel
Libraries and header files for developing applications that use appstream-glib.

%package debugger-common
Summary:        Common debugger pretty printers for Rust
BuildArch:      noarch

%description debugger-common
This package includes the common functionality for %{name}-gdb and %{name}-lldb.

%package gdb
Summary:        GDB pretty printers for Rust
BuildArch:      noarch
Requires:       gdb
Requires:       %{name}-debugger-common = 1.29.1-%{release}

%description gdb
This package includes the rust-gdb script, which allows easier debugging of Rust
programs.

%package -n cargo
Summary:        Rust's package manager and build tool
Version:        1.29.0
BuildRequires:  git
Requires:       rust
Provides:       bundled(libgit2) = 0.27 bundled(libssh2) = 1.8.1

%description -n cargo
Cargo is a tool that allows Rust projects to declare their various dependencies
and ensure that you'll always get a repeatable build.

%package -n rustfmt-preview
Summary:        Tool to find and fix Rust formatting issues
Version:        0.99.1
Requires:       cargo
Provides:       rustfmt = 0.99.1
Obsoletes:      rustfmt <= 0.9.0

%description -n rustfmt-preview
A tool for formatting Rust code according to style guidelines.

%package -n rls-preview
Summary:        Rust Language Server for IDE integration
Version:        0.130.0
Provides:       rls = 0.130.0 bundled(libgit2) = 0.27 bundled(libssh2) = 1.8.1
Requires:       rust-analysis %{name} = 1.29.1-%{release}

%description -n rls-preview
The Rust Language Server provides a server that runs in the background,
providing IDEs, editors, and other tools with information about Rust programs.
It supports functionality such as 'goto definition', symbol search,
reformatting, and code completion, and enables renaming and refactorings.

%package -n clippy-preview
Summary:        Lints to catch common mistakes and improve your Rust code
Version:        0.0.212
License:        MPLv2.0
Provides:       clippy = 0.0.212
Requires:       cargo %{name} = 1.29.1-%{release}

%description -n clippy-preview
A collection of lints to catch common mistakes and improve your Rust code.

%package src
Summary:        Sources for the Rust standard library
BuildArch:      noarch

%description src
This package includes source files for the Rust standard library.It may be
useful as a reference for code completion tools in various editors.

%package analysis
Summary:        Compiler analysis data for the Rust standard library
Requires:       rust-std-static = 1.29.1-%{release}

%description analysis
This package contains analysis data files produced with rustc's -Zsave-analysis
feature for the Rust standard library. The RLS (Rust Language Server) uses this
data to provide information about the Rust standard library.

%package help
Summary:     Help documents for rust

Provides:    %{name}-doc = %{version}-%{release} %{name}-cargo-doc = %{version}-%{release}
Obsoletes:   %{name}-doc < %{version}-%{release} %{name}-cargo-doc < %{version}-%{release}

%description help
Man pages and other related help documents for rust.

%prep
%autosetup -n rustc-1.29.1-src -p1

sed -i.try-py3 -e '/try python2.7/i try python3 "$@"' ./configure

rm -rf src/llvm-emscripten/
sed -e '/*\//q' src/libbacktrace/backtrace.h >src/libbacktrace/LICENSE-libbacktrace

sed -i.ignore -e '1i // ignore-test may still be exponential...' src/test/run-pass/issue-41696.rs

find src/vendor -name .cargo-checksum.json -exec sed -i.uncheck -e 's/"files":{[^}]*}/"files":{ }/' '{}' '+'

%build
%{?cmake_path:export PATH=%{cmake_path}:$PATH}
%{?library_path:export LIBRARY_PATH="%{library_path}"}
%{?rustflags:export RUSTFLAGS="-Clink-arg=-Wl,-z,relro,-z,now"}

%configure --disable-option-checking --libdir=%{_prefix}/lib \
  --build=%{rust_triple} --host=%{rust_triple} --target=%{rust_triple} \
  --local-rust-root=%{_prefix} --disable-jemalloc --disable-rpath \
  --enable-debuginfo --disable-debuginfo-only-std --enable-debuginfo-tools --disable-debuginfo-lines \
  --enable-extended --enable-vendor --enable-verbose-tests --release-channel=stable

python3 ./x.py build
python3 ./x.py doc

%install
%{?cmake_path:export PATH=%{cmake_path}:$PATH}
%{?library_path:export LIBRARY_PATH="%{library_path}"}
%{?rustflags:export RUSTFLAGS="-Clink-arg=-Wl,-z,relro,-z,now"}

DESTDIR=%{buildroot} python3 ./x.py install

install -d %{buildroot}%{_libdir}
find %{buildroot}%{_prefix}/lib -maxdepth 1 -type f -name '*.so' -exec mv -v -t %{buildroot}%{_libdir} '{}' '+'

find %{buildroot}%{_libdir} -maxdepth 1 -type f -name '*.so' -exec chmod -v +x '{}' '+'

(cd "%{buildroot}%{rustlibdir}/%{rust_triple}/lib" &&
 find ../../../../%{_lib} -maxdepth 1 -name '*.so' |
 while read lib; do
   cmp "$lib" "${lib##*/}"
   ln -v -f -s -t . "$lib"
 done)

find %{buildroot}%{rustlibdir} -maxdepth 1 -type f -exec rm -v '{}' '+'
find %{buildroot}%{rustlibdir} -type f -name '*.orig' -exec rm -v '{}' '+'
find %{buildroot}%{rustlibdir}/src -type f -name '*.py' -exec rm -v '{}' '+'
find %{buildroot}%{_docdir}/%{name}/html -empty -delete
find %{buildroot}%{_docdir}/%{name}/html -type f -exec chmod -x '{}' '+'

install -d %{buildroot}%{_datadir}/cargo/registry
install -d %{buildroot}%{_docdir}/cargo
ln -sT ../rust/html/cargo/ %{buildroot}%{_docdir}/cargo/html

%check
%{?cmake_path:export PATH=%{cmake_path}:$PATH}
%{?library_path:export LIBRARY_PATH="%{library_path}"}
%{?rustflags:export RUSTFLAGS="-Clink-arg=-Wl,-z,relro,-z,now"}

python3 ./x.py test --no-fail-fast || :
python3 ./x.py test --no-fail-fast cargo || :
python3 ./x.py test --no-fail-fast clippy || :
python3 ./x.py test --no-fail-fast rls || :
python3 ./x.py test --no-fail-fast rustfmt || :

%post
/sbin/ldconfig
%postun
/sbin/ldconfig

%files
%doc README.md
%license COPYRIGHT LICENSE-APACHE LICENSE-MIT
%license src/libbacktrace/LICENSE-libbacktrace
%license %{_docdir}/%{name}/html/*.txt
%dir %{rustlibdir}
%dir %{rustlibdir}/%{rust_triple}
%dir %{rustlibdir}/%{rust_triple}/lib
%{_bindir}/rustc
%{_bindir}/rustdoc
%{_libdir}/*.so
%{rustlibdir}/%{rust_triple}/lib/*.so
%{rustlibdir}/%{rust_triple}/codegen-backends/
%exclude %{_docdir}/%{name}/{README.md,COPYRIGHT,LICENSE,*.old}
%exclude %{_docdir}/%{name}/LICENSE-{APACHE,MIT,THIRD-PARTY}
%exclude %{rustlibdir}/etc/lldb_*.py*
%exclude %{_bindir}/rust-lldb

%files devel
%dir %{rustlibdir}
%dir %{rustlibdir}/%{rust_triple}
%dir %{rustlibdir}/%{rust_triple}/lib
%{rustlibdir}/%{rust_triple}/lib/*.rlib

%files debugger-common
%dir %{rustlibdir}
%dir %{rustlibdir}/etc
%{rustlibdir}/etc/debugger_*.py*

%files gdb
%{_bindir}/rust-gdb
%{rustlibdir}/etc/gdb_*.py*

%files -n cargo
%doc src/tools/cargo/README.md
%license src/tools/cargo/LICENSE-APACHE src/tools/cargo/LICENSE-MIT src/tools/cargo/LICENSE-THIRD-PARTY
%dir %{_datadir}/cargo
%dir %{_datadir}/cargo/registry
%{_bindir}/cargo
%{_sysconfdir}/bash_completion.d/cargo
%{_datadir}/zsh/site-functions/_cargo

%files -n rustfmt-preview
%doc src/tools/rustfmt/{README,CHANGELOG,Configurations}.md
%license src/tools/rustfmt/LICENSE-{APACHE,MIT}
%{_bindir}/rustfmt
%{_bindir}/cargo-fmt

%files -n rls-preview
%doc src/tools/rls/{README.md,COPYRIGHT,debugging.md}
%license src/tools/rls/LICENSE-{APACHE,MIT}
%{_bindir}/rls

%files -n clippy-preview
%doc src/tools/clippy/{README.md,CHANGELOG.md}
%license src/tools/clippy/LICENSE
%{_bindir}/cargo-clippy
%{_bindir}/clippy-driver

%files src
%dir %{rustlibdir}
%{rustlibdir}/src

%files analysis
%{rustlibdir}/%{rust_triple}/analysis/

%files help
%dir %{_docdir}/%{name}
%dir %{_docdir}/cargo
%dir %{_docdir}/%{name}/html
%docdir %{_docdir}/%{name}
%docdir %{_docdir}/cargo
%{_docdir}/%{name}/html/*/
%{_docdir}/%{name}/html/*.html
%{_docdir}/%{name}/html/*.css
%{_docdir}/%{name}/html/*.js
%{_docdir}/%{name}/html/*.svg
%{_docdir}/%{name}/html/*.woff
%{_docdir}/cargo/html
%{_mandir}/man1/rustc.1*
%{_mandir}/man1/rustdoc.1*
%{_mandir}/man1/cargo*.1*

%changelog
* Thu Dec 5 2019 wutao <wutao61@huawei.com> - 1.29.1-3
- Package init
