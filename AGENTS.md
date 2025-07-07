# AI Agent Guide for Alamo Drafthouse Feeds

This document provides guidance for AI agents working with the Alamo Drafthouse Feeds repository.

## Project Overview

This project generates JSON feeds for Alamo Drafthouse movie showings across multiple markets. It scrapes the Alamo Drafthouse API to create standardized JSON feeds that follow the [JSON Feed specification](https://jsonfeed.org/version/1.1).

## Repository Structure

```
├── drafthouse.py      # Main application code
├── pyproject.toml     # Project configuration and dependencies
├── README.md          # Project documentation
├── LICENSE           # MIT License
├── .github/          # GitHub Actions workflows
│   └── workflows/
│       ├── test.yml      # Test automation
│       ├── lint.yml      # Code linting
│       ├── merge.yml     # Merge automation
│       └── publish.yml   # Publishing automation
└── uv.lock           # Dependency lock file
```

## Key Technologies

- **Python 3.11+**: Core language requirement
- **uv**: Package manager and dependency resolution
- **click**: CLI framework
- **lru_cache**: Custom caching implementation
- **ruff**: Code linting and formatting
- **mypy**: Type checking

## Supported Markets

The application supports the following Alamo Drafthouse markets:
- `chicago`
- `los-angeles`
- `nyc`
- `sf`

## Development Setup

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Run the application**:
   ```bash
   uv run drafthouse <market>
   ```

3. **Example usage**:
   ```bash
   uv run drafthouse sf > sf.json
   ```

## Code Structure

### Main Components

- **`FeedItem`**: TypedDict defining individual feed items
- **`Feed`**: TypedDict defining the complete feed structure
- **`main()`**: CLI entry point with click decorators
- **`_get_json()`**: HTTP request utility
- **`_sort_presentations()`**: Sorting logic for presentations
- **`_item_opening_date()`**: Date parsing and caching

### API Integration

The application fetches data from:
```
https://drafthouse.com/s/mother/v2/schedule/market/{market}
```

### Output Format

Generates JSON feeds compatible with JSON Feed 1.1 specification:
- Feed metadata (title, URLs, icon)
- Array of items with movie information
- HTML content including images and descriptions

## Testing

### Run Tests
```bash
uv run drafthouse sf
```

### Linting
```bash
ruff check .
```

### Type Checking
```bash
mypy .
```

## GitHub Actions

- **Test**: Runs application against SF market
- **Lint**: Runs ruff for code quality
- **Merge**: Handles merge automation
- **Publish**: Handles package publishing

## Working with the Code

### Adding New Markets

1. Add market identifier to `_MARKETS` list
2. Ensure the market exists in Alamo Drafthouse API
3. Test with the new market

### Modifying Feed Structure

1. Update `FeedItem` or `Feed` TypedDict definitions
2. Modify corresponding data processing logic
3. Ensure JSON Feed specification compliance

### Cache Management

The application uses LRU cache for:
- Opening date information
- Feed metadata persistence

### Error Handling

- HTTP requests have 10-second timeout
- Image URL validation with logging
- Assertion for non-empty feed items

## Common Operations

### Generate Feed for Specific Market
```bash
uv run drafthouse chicago -o chicago.json
```

### Enable Verbose Logging
```bash
uv run drafthouse sf --verbose
```

### Use Custom Cache
```bash
uv run drafthouse nyc --cache-path /tmp/cache --cache-max 200
```

## Dependencies

### Production Dependencies
- `click>=8.1.1,<9.0`: CLI framework
- `lru-cache`: Custom caching (from GitHub release)

### Development Dependencies
- `mypy>=1.0.0,<2.0`: Type checking
- `ruff>=0.3.0`: Linting and formatting

## Best Practices

1. **Type Safety**: Use mypy for type checking
2. **Code Quality**: Follow ruff linting rules
3. **Error Handling**: Log warnings for unexpected conditions
4. **Caching**: Use persistent cache for API responses
5. **Testing**: Verify feeds generate successfully

## Troubleshooting

### Common Issues

1. **Module not found**: Run `uv sync` to install dependencies
2. **API timeouts**: Check network connectivity
3. **Empty feeds**: Verify market name and API availability
4. **Type errors**: Run `mypy` for type checking

### Debug Mode

Enable verbose logging to see detailed API requests:
```bash
uv run drafthouse sf --verbose
```

## Contributing

1. Follow existing code style (ruff configuration)
2. Maintain type annotations
3. Test with multiple markets
4. Update this guide for significant changes