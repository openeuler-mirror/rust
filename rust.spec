%global rust_arches x86_64 aarch64
%global bootstrap_rust 1.29.1
%global bootstrap_cargo 1.29.0
%global bootstrap_channel %{bootstrap_rust}
%global bootstrap_date 2018-10-12

Name:           rust
Version:        1.30.0
Release:        1
Summary:        The Rust Programming Language
License:        (ASL 2.0 or MIT) and (BSD and MIT)
URL:            https://www.rust-lang.org
ExclusiveArch:  aarch64 x86_64
Source0:        https://static.rust-lang.org/dist/rustc-1.30.0-src.tar.xz

%{lua: function rust_triple(arch)
  local abi = "gnu"
  return arch.."-unknown-linux-"..abi
end}
%global rust_triple %{lua: print(rust_triple(rpm.expand("%{_target_cpu}")))}

BuildRequires:  cargo >= %{bootstrap_cargo}
BuildRequires:  (%{name} >= %{bootstrap_rust} with %{name} <= 1.30.0)
BuildRequires:  make gdb gcc gcc-c++ ncurses-devel curl
BuildRequires:  pkgconfig(libcurl) pkgconfig(liblzma)
BuildRequires:  pkgconfig(openssl) pkgconfig(zlib)
BuildRequires:  pkgconfig(libgit2) >= 0.27 pkgconfig(libssh2) >= 1.6.0
BuildRequires:  python3 cmake >= 2.8.11 llvm-devel >= 5.0
BuildRequires:  llvm-static libffi-devel procps-ng
Provides:       bundled(libbacktrace) = 8.1.0 bundled(miniz) = 1.16~beta+r1
Provides:       rustc = 1.30.0-%{release}
Requires:       %{name}-std-static = 1.30.0-%{release} /usr/bin/cc

%global _privatelibs lib(.*-[[:xdigit:]]{16}*|rustc.*)[.]so.*
%global __provides_exclude ^(%{_privatelibs})$
%global __requires_exclude ^(%{_privatelibs})$
%global __provides_exclude_from ^(%{_docdir}|%{rustlibdir}/src)/.*$
%global __requires_exclude_from ^(%{_docdir}|%{rustlibdir}/src)/.*$
%global _find_debuginfo_opts --keep-section .rustc
%global rustflags -Clink-arg=-Wl,-z,relro,-z,now

%description
Rust is a systems programming language focused on three goals:safety,
speed,and concurrency.It maintains these goals without having
a garbage
collector, making it a useful language for a number of use cases other
languages are not good at: embedding in other languages, programs with
specific space and time requirements,and writing low-level code, like
device drivers and operating systems. It improves on current languages
targeting this space by having a number of compile-time safety checks
that produce no runtime overhead,while eliminating all data races.

%package devel
Summary:             Libraries and header files for developing applications that use appstream-glib
Provides:            rust-std-static = %{version}-%{release}
Obsoletes:           rust-std-static < %{version}-%{release}
%description devel
Libraries and header files for developing applications that use appstream-glib.

%package debugger-common
Summary:             Common debugger pretty printers for Rust
BuildArch:           noarch
%description debugger-common
This package includes the common functionality for rust-gdb and rust-lldb.

%package gdb
Summary:             GDB pretty printers for Rust
BuildArch:           noarch
Requires:            gdb rust-debugger-common = 1.30.0-%{release}
%description gdb
This package includes the rust-gdb script, which allows easier debugging of Rust
programs.

%package lldb
Summary:             LLDB pretty printers for Rust
Requires:            lldb python2-lldb rust-debugger-common = 1.30.0-%{release}
%description lldb
This package includes the rust-lldb script, which allows easier debugging of Rust
programs.

%package help
Summary:             Help documentation for Rust
Provides:            rust-doc = %{version}-%{release} cargo-doc = %{version}-%{release}
Obsoletes:           rust-doc < %{version}-%{release} cargo-doc < %{version}-%{release}
%description help
Man pages and other related help documents for rust.

%package -n cargo
Summary:             Rust's package manager and build tool
Version:             1.30.0
BuildRequires:       git
Provides:            bundled(libgit2)= 0.27
Requires:            rust
%description -n cargo
Cargo is a tool that allows Rust projects to declare their various dependencies
and ensure that you'll always get a repeatable build.


%package -n rustfmt-preview
Summary:             Tool to find and fix Rust formatting issues
Version:             0.99.4
Requires:            cargo
Obsoletes:           rustfmt <= 0.9.0
Provides:            rustfmt = 0.99.4
%description -n rustfmt-preview
A tool for formatting Rust code according to style guidelines.

%package -n rls-preview
Summary:             Rust Language Server for IDE integration
Version:             0.130.5
Provides:            rls = 0.130.5
Provides:            bundled(libgit2) = 0.27
Requires:            rust-analysis rust = 1.30.0-%{release}
%description -n rls-preview
The Rust Language Server provides a server that runs in the background,
providing IDEs, editors, and other tools with information about Rust programs.
It supports functionality such as 'goto definition', symbol search,
reformatting, and code completion, and enables renaming and refactorings.

%package -n clippy-preview
Summary:             Lints to catch common mistakes and improve your Rust code
Version:             0.0.212
License:             MPLv2.0
Provides:            clippy = 0.0.212
Requires:            cargo rust = 1.30.0-%{release}
%description -n clippy-preview
A collection of lints to catch common mistakes and improve your Rust code.

%package src
Summary:             Sources for the Rust standard library
BuildArch:           noarch
%description src
This package includes source files for the Rust standard library.  It may be
useful as a reference for code completion tools in various editors.

%package analysis
Summary:             Compiler analysis data for the Rust standard library
Requires:            devel = 1.30.0-%{release}
%description analysis
This package contains analysis data files produced with rustc's -Zsave-analysis
feature for the Rust standard library. The RLS (Rust Language Server) uses this
data to provide information about the Rust standard library.

%prep
%autosetup -n rustc-1.30.0-src -p1
sed -i.try-py3 -e '/try python2.7/i try python3 "$@"' ./configure
rm -rf src/llvm src/llvm-emscripten/ src/tools/clang src/tools/lld src/tools/lldb
sed -e '/*\//q' src/libbacktrace/backtrace.h \
  >src/libbacktrace/LICENSE-libbacktrace
find src/vendor -name .cargo-checksum.json \
 -exec sed -i.uncheck -e 's/"files":{[^}]*}/"files":{ }/' '{}' '+'

%build
export LIBSSH2_SYS_USE_PKG_CONFIG=1
export RUSTFLAGS="-Clink-arg=-Wl,-z,relro,-z,now"
%global common_libdir %{_prefix}/lib
%global rustlibdir %{common_libdir}/rustlib
%define enable_debuginfo --enable-debuginfo --disable-debuginfo-only-std --enable-debuginfo-tools --disable-debuginfo-lines
%configure --disable-option-checking \
  --libdir=%{common_libdir}  --release-channel=stable \
  --build=%{rust_triple} --host=%{rust_triple} --target=%{rust_triple} \
  --local-rust-root=%{_prefix} --enable-verbose-tests \
  --llvm-root=%{_prefix} --disable-codegen-tests \
  --enable-llvm-link-shared --enable-vendor \
  --disable-jemalloc -disable-rpath \
  %{enable_debuginfo} --enable-extended 
python3 ./x.py build
python3 ./x.py doc

%install
export RUSTFLAGS="-Clink-arg=-Wl,-z,relro,-z,now"
DESTDIR=%{buildroot} python3 ./x.py install
mkdir -p %{buildroot}%{_libdir}
find %{buildroot}%{common_libdir} -maxdepth 1 -type f -name '*.so' \
  -exec mv -v -t %{buildroot}%{_libdir} '{}' '+'
find %{buildroot}%{_libdir} -maxdepth 1 -type f -name '*.so' \
  -exec chmod -v +x '{}' '+'
(cd "%{buildroot}%{rustlibdir}/%{rust_triple}/lib" &&
 find ../../../../%{_lib} -maxdepth 1 -name '*.so' |
 while read lib; do
   cmp "$lib" "${lib##*/}"
   ln -v -f -s -t . "$lib"
 done)
find %{buildroot}%{rustlibdir} -maxdepth 1 -type f -exec rm -v '{}' '+'
find %{buildroot}%{rustlibdir} -type f -name '*.orig' -exec rm -v '{}' '+'
find %{buildroot}%{rustlibdir}/src -type f -name '*.py' -exec rm -v '{}' '+'
rm -f %{buildroot}%{_docdir}/rust/{README.md,COPYRIGHT,LICENSE,LICENSE-APACHE}
rm -f %{buildroot}%{_docdir}/rust/{LICENSE-MIT,LICENSE-THIRD-PARTY,*.old}
find %{buildroot}%{_docdir}/rust/html -empty -delete
find %{buildroot}%{_docdir}/rust/html -type f -exec chmod -x '{}' '+'
install -d %{buildroot}%{_datadir}/cargo/registry
install -d %{buildroot}%{_docdir}/cargo
ln -sT ../rust/html/cargo/ %{buildroot}%{_docdir}/cargo/html

%check
export RUSTFLAGS="-Clink-arg=-Wl,-z,relro,-z,now"
python3 ./x.py test --no-fail-fast || :
python3 ./x.py test --no-fail-fast cargo || :
python3 ./x.py test --no-fail-fast clippy || :
python3 ./x.py test --no-fail-fast rls || :
python3 ./x.py test --no-fail-fast rustfmt || :
%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig

%files
%license COPYRIGHT LICENSE-APACHE LICENSE-MIT
%license src/libbacktrace/LICENSE-libbacktrace
%{_bindir}/{rustc,rustdoc}
%{_libdir}/*.so
%{_mandir}/man1/{rustc.1*,rustdoc.1*}
%dir %{rustlibdir}/%{rust_triple}/lib
%{rustlibdir}/%{rust_triple}/lib/*.so
%{rustlibdir}/%{rust_triple}/codegen-backends/

%files devel
%dir %{rustlibdir}/%{rust_triple}/lib
%{rustlibdir}/%{rust_triple}/lib/*.rlib

%files debugger-common
%dir %{rustlibdir}/etc
%{rustlibdir}/etc/debugger_*.py*

%files gdb
%{_bindir}/rust-gdb
%{rustlibdir}/etc/gdb_*.py*

%files lldb
%{_bindir}/rust-lldb
%{rustlibdir}/etc/lldb_*.py*

%files help
%doc README.md
%{_docdir}/cargo/html
%{_mandir}/man1/cargo*.1*
%doc %{_docdir}/rust/html/*.txt
%docdir %{_docdir}/{rust,cargo}
%dir %{_docdir}/{rust/html,cargo}
%{_docdir}/rust/html/{*/,*.html,*.css,*.js,*.svg,*.woff}
%doc src/tools/rustfmt/{README,CHANGELOG,Configurations}.md
%doc src/tools/rls/{README.md,COPYRIGHT,debugging.md}
%doc src/tools/clippy/{README.md,CHANGELOG.md}

%files -n cargo
%doc src/tools/cargo/README.md src/tools/cargo/LICENSE-THIRD-PARTY
%doc src/tools/cargo/LICENSE-APACHE src/tools/cargo/LICENSE-MIT
%{_bindir}/cargo
%dir %{_datadir}/cargo/registry
%{_sysconfdir}/bash_completion.d/cargo
%{_datadir}/zsh/site-functions/_cargo

%files -n rustfmt-preview
%{_bindir}/{rustfmt,cargo-fmt}
%doc src/tools/rustfmt/LICENSE-{APACHE,MIT}

%files -n rls-preview
%{_bindir}/rls
%doc src/tools/rls/LICENSE-{APACHE,MIT}

%files -n clippy-preview
%{_bindir}/{cargo-clippy,clippy-driver}
%doc src/tools/clippy/LICENSE

%files src
%{rustlibdir}/src

%files analysis
%{rustlibdir}/%{rust_triple}/analysis/

%changelog
* Fri Jun 5 2020 yaokai <yaoaki13@huawei.com> - 1.30.0-1
- Update to 1.30.0-1
* Thu Dec 5 2019 wutao <wutao61@huawei.com> - 1.29.1-3
- Package init
