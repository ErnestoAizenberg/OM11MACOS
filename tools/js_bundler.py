import hashlib
import json
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set

from py_mini_racer import MiniRacer


class JSBundler:
    def __init__(
        self,
        entry_point: str,
        output_path: str = "bundle.js",
        exclude_modules: Optional[List[str]] = None,
        cache_dir: str = ".js_bundler_cache",
        validate_js: bool = True,
        log_level: str = "INFO",
    ):
        self.entry_point = os.path.abspath(entry_point)
        self.output_path = os.path.abspath(output_path)
        self.exclude_modules = exclude_modules or []
        self.cache_dir = cache_dir
        self.validate_js = validate_js
        self.js_engine = MiniRacer() if validate_js else None

        # Настройка логирования
        self._setup_logging(log_level)
        self.logger = logging.getLogger("JSBundler")

        # Граф зависимостей и кеш
        self.dependency_graph: Dict[str, List[str]] = {}
        self.processed_files: Set[str] = set()
        self.file_hashes: Dict[str, str] = {}

        # Создаем директорию для кеша
        os.makedirs(self.cache_dir, exist_ok=True)
        self.logger.debug(f"Initialized bundler with entry point: {self.entry_point}")

    def _setup_logging(self, level: str):
        """Настраивает систему логирования."""
        logging.basicConfig(
            level=getattr(logging, level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.StreamHandler(), logging.FileHandler("js_bundler.log")],
        )

    def _validate_js(self, code: str, context: str = "") -> bool:
        """Проверяет валидность JS-кода с помощью py_mini_racer."""
        if not self.validate_js or not self.js_engine:
            return True

        try:
            self.js_engine.eval(code)
            return True
        except Exception as e:
            self.logger.error(f"JS validation error in {context}: {str(e)}")
            return False

    def _resolve_path(self, module_path: str, parent_path: str) -> Optional[str]:
        """Разрешает путь к модулю с подробным логированием."""
        self.logger.debug(f"Resolving module: {module_path} from {parent_path}")

        if module_path in self.exclude_modules:
            self.logger.debug(f"Ignoring excluded module: {module_path}")
            return None

        # Абсолютный путь
        if os.path.isabs(module_path):
            if os.path.exists(module_path):
                self.logger.debug(f"Resolved absolute path: {module_path}")
                return module_path

            # Проверяем с расширениями
            for ext in ["", ".js", ".mjs"]:
                if os.path.exists(module_path + ext):
                    resolved = module_path + ext
                    self.logger.debug(f"Resolved with extension {ext}: {resolved}")
                    return resolved

            self.logger.warning(f"Absolute path not found: {module_path}")
            return None

        # Относительный путь
        if module_path.startswith(("./", "../")):
            abs_path = os.path.normpath(
                os.path.join(os.path.dirname(parent_path), module_path)
            )

            # Проверяем возможные варианты
            for ext in ["", ".js", ".mjs"]:
                test_path = abs_path + ext
                if os.path.exists(test_path):
                    self.logger.debug(f"Resolved relative path: {test_path}")
                    return test_path

                index_path = os.path.join(abs_path, f"index{ext}")
                if os.path.exists(index_path):
                    self.logger.debug(f"Resolved index file: {index_path}")
                    return index_path

            self.logger.warning(
                f"Relative path not found: {abs_path} (from {module_path})"
            )
            return None

        # Поиск в node_modules
        current_dir = os.path.dirname(parent_path)
        search_paths = []

        while True:
            node_modules = os.path.join(current_dir, "node_modules")
            if os.path.exists(node_modules):
                module_abs_path = os.path.join(node_modules, module_path)
                package_json = os.path.join(module_abs_path, "package.json")

                if os.path.exists(package_json):
                    try:
                        with open(package_json, "r") as f:
                            pkg = json.load(f)
                            main_file = pkg.get("main", "index.js")
                            resolved = os.path.join(module_abs_path, main_file)
                            if os.path.exists(resolved):
                                self.logger.debug(
                                    f"Resolved via package.json: {resolved}"
                                )
                                return resolved
                    except (json.JSONDecodeError, IOError) as e:
                        self.logger.warning(
                            f"Error reading package.json: {package_json} - {str(e)}"
                        )

                # Проверяем стандартные варианты
                for ext in ["", ".js", ".mjs"]:
                    test_path = module_abs_path + ext
                    if os.path.exists(test_path):
                        self.logger.debug(f"Resolved node_modules path: {test_path}")
                        return test_path

                    index_path = os.path.join(module_abs_path, f"index{ext}")
                    if os.path.exists(index_path):
                        self.logger.debug(f"Resolved node_modules index: {index_path}")
                        return index_path

                search_paths.append(module_abs_path)

            # Поднимаемся на уровень выше
            parent_dir = os.path.dirname(current_dir)
            if parent_dir == current_dir:
                break
            current_dir = parent_dir

        self.logger.warning(
            f"Module not found in node_modules: {module_path}. Searched in: {search_paths}"
        )
        return None

    def _parse_imports(self, content: str) -> List[str]:
        """Извлекает все импорты с улучшенным парсингом."""
        imports = set()

        # Все шаблоны импортов
        patterns = [
            # import { x } from 'y'
            (r'import\s*\{([^}]+)\}\s*from\s*[\'"]([^\'"]+)[\'"]', 2),
            # import x from 'y'
            (r'import\s+([\w*]+)\s+from\s*[\'"]([^\'"]+)[\'"]', 2),
            # import * as x from 'y'
            (r'import\s*\*\s*as\s+(\w+)\s+from\s*[\'"]([^\'"]+)[\'"]', 2),
            # import 'x'
            (r'import\s*[\'"]([^\'"]+)[\'"]', 1),
            # import('x')
            (r'import\([\'"]([^\'"]+)[\'"]\)', 1),
            # require('x')
            (r'require\([\'"]([^\'"]+)[\'"]\)', 1),
        ]

        for pattern, group in patterns:
            matches = re.finditer(pattern, content, re.MULTILINE)
            for match in matches:
                imports.add(match.group(group))
                self.logger.debug(
                    f"Found import: {match.group(group)} (pattern: {pattern})"
                )

        return sorted(list(imports))

    def _build_dependency_graph(self, file_path: str):
        """Строит граф зависимостей с защитой от циклических зависимостей."""
        if file_path in self.dependency_graph:
            return

        self.logger.info(f"Building dependencies for: {file_path}")
        self.dependency_graph[file_path] = []

        try:
            content = self._read_file(file_path)
            imports = self._parse_imports(content)

            for imp in imports:
                resolved = self._resolve_path(imp, file_path)
                if not resolved:
                    if imp not in self.exclude_modules:
                        self.logger.warning(
                            f"Unresolved dependency: '{imp}' in {file_path}"
                        )
                    continue

                # Проверка на циклические зависимости
                if resolved == file_path:
                    self.logger.error(
                        f"Circular dependency detected: {file_path} imports itself"
                    )
                    continue

                self.dependency_graph[file_path].append(resolved)
                if resolved not in self.dependency_graph:
                    self._build_dependency_graph(resolved)

        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {str(e)}")
            raise

    def _read_file(self, file_path: str) -> str:
        """Читает файл с обработкой ошибок и валидацией."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                normalized = content.replace("\r\n", "\n").replace("\r", "\n")

                # Базовая валидация JS
                if self.validate_js and not self._validate_js(
                    normalized, f"file {file_path}"
                ):
                    self.logger.warning(f"Potential JS syntax issues in {file_path}")

                return normalized

        except IOError as e:
            self.logger.error(f"Failed to read file {file_path}: {str(e)}")
            raise RuntimeError(f"File read error: {file_path}") from e

    def _get_cache_key(self, file_path: str) -> str:
        """Генерирует ключ кеша с проверкой изменений."""
        try:
            content = self._read_file(file_path)
            return hashlib.sha256(content.encode("utf-8")).hexdigest()
        except Exception as e:
            self.logger.error(f"Failed to generate cache key for {file_path}: {str(e)}")
            return ""

    def _load_from_cache(self, file_path: str) -> Optional[str]:
        """Загружает из кеша с проверкой валидности."""
        if not os.path.exists(self.cache_dir):
            return None

        cache_key = self._get_cache_key(file_path)
        if not cache_key:
            return None

        cache_file = os.path.join(self.cache_dir, f"{cache_key}.js")

        if os.path.exists(cache_file):
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    cached = f.read()
                    if self.validate_js and not self._validate_js(
                        cached, f"cached {file_path}"
                    ):
                        self.logger.warning(
                            f"Invalid cached content for {file_path}, rebuilding..."
                        )
                        return None
                    return cached
            except IOError as e:
                self.logger.warning(f"Failed to read cache for {file_path}: {str(e)}")

        return None

    def _save_to_cache(self, file_path: str, processed_code: str):
        """Сохраняет в кеш с обработкой ошибок."""
        cache_key = self._get_cache_key(file_path)
        if not cache_key:
            return

        cache_file = os.path.join(self.cache_dir, f"{cache_key}.js")

        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(processed_code)
        except IOError as e:
            self.logger.error(f"Failed to write cache for {file_path}: {str(e)}")

    def _transform_imports(self, content: str, file_path: str) -> str:
        """Трансформирует импорты с улучшенной обработкой ошибок."""
        transformations = [
            # import { x } from 'y' -> const {x} = __module_y
            (
                r'import\s*\{([^}]+)\}\s*from\s*[\'"]([^\'"]+)[\'"]',
                lambda m: self._replace_import(m, file_path, named=True),
            ),
            # import x from 'y' -> const x = __module_y.default
            (
                r'import\s+([\w*]+)\s+from\s*[\'"]([^\'"]+)[\'"]',
                lambda m: self._replace_import(m, file_path, default=True),
            ),
            # import * as x from 'y' -> const x = __module_y
            (
                r'import\s*\*\s*as\s+(\w+)\s+from\s*[\'"]([^\'"]+)[\'"]',
                lambda m: self._replace_import(m, file_path, namespace=True),
            ),
            # import 'x' -> __module_x
            (
                r'import\s*[\'"]([^\'"]+)[\'"]',
                lambda m: self._replace_import(m, file_path, side_effect=True),
            ),
            # import('x') -> Promise.resolve(__module_x)
            (
                r'import\([\'"]([^\'"]+)[\'"]\)',
                lambda m: self._replace_import(m, file_path, dynamic=True),
            ),
            # require('x') -> __module_x
            (
                r'require\([\'"]([^\'"]+)[\'"]\)',
                lambda m: self._replace_import(m, file_path, require=True),
            ),
        ]

        for pattern, replacer in transformations:
            try:
                content = re.sub(pattern, replacer, content)
            except Exception as e:
                self.logger.error(
                    f"Error transforming imports in {file_path}: {str(e)}"
                )
                raise

        return content

    def _replace_import(
        self,
        match: re.Match,
        parent_path: str,
        named=False,
        default=False,
        namespace=False,
        side_effect=False,
        dynamic=False,
        require=False,
    ) -> str:
        """Обрабатывает все типы импортов."""
        try:
            module_path = (
                match.group(2) if (named or default or namespace) else match.group(1)
            )
            resolved = self._resolve_path(module_path, parent_path)

            if not resolved:
                if module_path not in self.exclude_modules:
                    self.logger.warning(
                        f"Unresolved import: {module_path} in {parent_path}"
                    )
                return match.group(0)  # Оставляем оригинальный импорт

            module_name = Path(resolved).stem.replace(".", "_")

            if named:
                imported_items = match.group(1).strip()
                return f"const {{{imported_items}}} = __module_{module_name}"
            elif default:
                import_name = match.group(1)
                return f"const {import_name} = __module_{module_name}.default"
            elif namespace:
                import_name = match.group(1)
                return f"const {import_name} = __module_{module_name}"
            elif dynamic:
                return f"Promise.resolve(__module_{module_name})"
            else:  # side_effect или require
                return f"__module_{module_name}"

        except Exception as e:
            self.logger.error(f"Error processing import: {match.group(0)}: {str(e)}")
            return match.group(0)

    def _process_module(self, file_path: str) -> str:
        """Обрабатывает модуль с улучшенной обработкой ошибок."""
        try:
            cached = self._load_from_cache(file_path)
            if cached:
                self.logger.debug(f"Using cached version of {file_path}")
                return cached

            content = self._read_file(file_path)
            module_name = Path(file_path).stem.replace(".", "_")

            # Трансформируем импорты
            content = self._transform_imports(content, file_path)

            # Создаем обертку IIFE
            wrapped = f"// Module: {file_path}\n"
            wrapped += f"const __module_{module_name} = (() => {{\n"
            wrapped += "  const exports = {};\n"
            wrapped += "  const module = { exports };\n\n"
            wrapped += content + "\n\n"
            wrapped += "  return module.exports;\n}})();\n\n"

            # Валидация результата
            if self.validate_js and not self._validate_js(
                wrapped, f"processed {file_path}"
            ):
                self.logger.error(f"Generated invalid JS for {file_path}")
                raise RuntimeError(f"Invalid JS generated for {file_path}")

            self._save_to_cache(file_path, wrapped)
            return wrapped

        except Exception as e:
            self.logger.error(f"Failed to process module {file_path}: {str(e)}")
            raise

    def bundle(self) -> str:
        """Основной метод сборки с полной обработкой ошибок."""
        try:
            self.logger.info("Starting bundle process...")

            # 1. Построение графа зависимостей
            self._build_dependency_graph(self.entry_point)
            self.logger.debug(
                f"Dependency graph: {json.dumps(self.dependency_graph, indent=2)}"
            )

            # 2. Топологическая сортировка
            sorted_modules = self._topological_sort()
            self.logger.info(f"Processing modules in order: {sorted_modules}")

            # 3. Обработка модулей
            bundled_code = "// Bundled by JS Bundler (with validation)\n"
            bundled_code += "(function() {\n\n"

            for module in sorted_modules:
                if module not in self.processed_files:
                    self.logger.info(f"Processing module: {module}")
                    try:
                        module_code = self._process_module(module)
                        bundled_code += module_code
                        self.processed_files.add(module)
                    except Exception:
                        self.logger.error(f"Skipping module {module} due to errors")
                        continue

            # 4. Запуск приложения
            main_module = Path(self.entry_point).stem.replace(".", "_")
            bundled_code += "\n// Application entry point\n"
            bundled_code += f"const __main = __module_{main_module};\n"
            bundled_code += "if (typeof window !== 'undefined') window.app = __main;\n"
            bundled_code += "if (typeof module !== 'undefined' && module.exports) module.exports = __main;\n"
            bundled_code += "\n})();\n"

            # Финальная валидация
            if self.validate_js and not self._validate_js(bundled_code, "final bundle"):
                self.logger.error("Final bundle validation failed!")
                raise RuntimeError("Generated invalid JS bundle")

            # Сохранение результата
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            with open(self.output_path, "w", encoding="utf-8") as f:
                f.write(bundled_code)

            self.logger.info(f"Successfully bundled to {self.output_path}")
            return bundled_code

        except Exception as e:
            self.logger.error(f"Bundle failed: {str(e)}")
            raise

    def _topological_sort(self) -> List[str]:
        """Топологическая сортировка с обнаружением циклов."""
        visited = set()
        temp_visited = set()
        result = []
        cycles = []

        def visit(node):
            if node in temp_visited:
                cycles.append(node)
                return
            if node in visited:
                return

            temp_visited.add(node)
            for neighbor in self.dependency_graph.get(node, []):
                visit(neighbor)
            temp_visited.remove(node)
            visited.add(node)
            result.append(node)

        for node in list(self.dependency_graph.keys()):
            visit(node)

        if cycles:
            cycle_msg = "Circular dependencies detected: " + " -> ".join(cycles)
            self.logger.error(cycle_msg)
            raise RuntimeError(cycle_msg)

        return result[::-1]


if __name__ == "__main__":
    try:
        bundler = JSBundler(
            entry_point="./src/main.js",
            output_path="./dist/bundle.js",
            exclude_modules=["fs", "path", "http"],
            validate_js=True,
            log_level="DEBUG",
        )

        result = bundler.bundle()
        print(f"✅ Bundle created successfully at {bundler.output_path}")

    except Exception as e:
        print(f"❌ Bundle failed: {str(e)}")
        exit(1)
