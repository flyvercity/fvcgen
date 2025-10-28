"""Test script for FVC Generator."""

import sys


from fvc.gen.config import Config
from fvc.gen.generator import validate_fvc_config, FVCGenerator
from fvc.gen.utils import generate_config_template


def main():
    """Test the application."""
    print('Testing FVC Generator...')

    try:
        # Test template generation
        print('Generating configuration template...')
        generate_config_template('test_config.yaml')
        print('✓ Template generated successfully')

        # Test configuration loading
        print('Testing configuration loading...')

        config = Config.from_file('test_config.yaml')
        print('✓ Configuration loaded successfully')

        # Test validation
        print('Testing configuration validation...')

        is_valid = validate_fvc_config(config)
        if is_valid:
            print('✓ Configuration validation passed')
        else:
            print('✗ Configuration validation failed')
            return False

        # Test FVC generation
        print('Testing FVC generation...')

        generator = FVCGenerator(config)
        generator.generate()
        print('✓ FVC generation completed')

        print('\n🎉 All tests passed!')
        return True

    except Exception as e:
        print(f'✗ Test failed: {e}')
        import traceback

        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
