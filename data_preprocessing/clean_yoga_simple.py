#!/usr/bin/env python3
"""
Simple Yoga Dataset Cleaning Demo

This standalone script demonstrates the data cleaning functionality
without complex imports.
"""

import json
import logging
import re
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional


def clean_string(value: str) -> Optional[str]:
    """Clean and normalize string values."""
    if not value or not isinstance(value, str):
        return None
    
    cleaned = value.strip()
    if not cleaned or cleaned == " Pose":
        return None
    
    return cleaned


def clean_pose_types(pose_types: List[str]) -> List[str]:
    """Clean and validate pose types."""
    if not pose_types or not isinstance(pose_types, list):
        return []
    
    cleaned_types = []
    for pose_type in pose_types:
        cleaned_type = clean_string(pose_type)
        if cleaned_type:
            cleaned_types.append(cleaned_type)
    
    return cleaned_types


def clean_followup_poses(followup_poses) -> List[str]:
    """Clean and validate followup poses."""
    if not followup_poses or followup_poses is None:
        return []
    
    if isinstance(followup_poses, list):
        cleaned_poses = []
        for pose in followup_poses:
            cleaned_pose = clean_string(pose)
            if cleaned_pose:
                cleaned_poses.append(cleaned_pose)
        return cleaned_poses
    
    return []


def validate_url(url: str) -> bool:
    """Validate if URL is properly formatted."""
    if not url:
        return False
    
    url_pattern = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return url_pattern.match(url) is not None


def is_valid_record(row_data: Dict[str, Any]) -> bool:
    """Check if a record has minimum required fields."""
    name = clean_string(row_data.get('name', ''))
    pose_types = clean_pose_types(row_data.get('pose_type', []))
    return bool(name and pose_types)


def clean_record(row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Clean a single record and prepare it for Qdrant."""
    row_data = row.get('row', {})
    
    if not is_valid_record(row_data):
        return None
    
    cleaned_record = {
        'id': str(uuid.uuid4()),
        'name': clean_string(row_data.get('name', '')),
        'sanskrit_name': clean_string(row_data.get('sanskrit_name', '')),
        'expertise_level': clean_string(row_data.get('expertise_level', '')) or 'Unknown',
        'pose_type': clean_pose_types(row_data.get('pose_type', [])),
        'followup_poses': clean_followup_poses(row_data.get('followup_poses')),
        'photo_url': clean_string(row_data.get('photo_url', ''))
    }
    
    # Validate photo URL
    if cleaned_record['photo_url'] and not validate_url(cleaned_record['photo_url']):
        cleaned_record['photo_url'] = None
    
    # Create searchable text
    searchable_text_parts = [
        cleaned_record['name'],
        cleaned_record['sanskrit_name'],
        cleaned_record['expertise_level'],
        ' '.join(cleaned_record['pose_type']),
        ' '.join(cleaned_record['followup_poses'])
    ]
    
    cleaned_record['searchable_text'] = ' '.join(
        part for part in searchable_text_parts if part
    ).strip()
    
    # Add metadata
    cleaned_record['metadata'] = {
        'has_followup_poses': len(cleaned_record['followup_poses']) > 0,
        'has_photo': bool(cleaned_record['photo_url'])
    }
    
    return cleaned_record


def clean_yoga_dataset(input_file: str, output_file: str = None):
    """Clean the yoga dataset and save results."""
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"❌ Input file not found: {input_file}")
        return False
    
    # Load data
    try:
        with open(input_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        print(f"✅ Loaded dataset with {len(data.get('rows', []))} records")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return False
    
    # Clean records
    rows = data.get('rows', [])
    cleaned_data = []
    stats = {
        'total_records': len(rows),
        'cleaned_records': 0,
        'removed_records': 0
    }
    
    for row in rows:
        cleaned_record = clean_record(row)
        if cleaned_record:
            cleaned_data.append(cleaned_record)
            stats['cleaned_records'] += 1
        else:
            stats['removed_records'] += 1
    
    # Save cleaned data
    if not output_file:
        output_file = input_path.parent / f"cleaned_{input_path.name}"
    
    output_data = {
        'metadata': {
            'total_records': stats['cleaned_records'],
            'source_file': str(input_path),
            'cleaning_stats': stats
        },
        'records': cleaned_data
    }
    
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(output_data, file, indent=2, ensure_ascii=False)
        print(f"✅ Cleaned data saved to: {output_file}")
    except Exception as e:
        print(f"❌ Error saving cleaned data: {e}")
        return False
    
    # Print statistics
    print("\n" + "="*50)
    print("YOGA DATASET CLEANING STATISTICS")
    print("="*50)
    print(f"Total records processed: {stats['total_records']}")
    print(f"Successfully cleaned: {stats['cleaned_records']}")
    print(f"Records removed: {stats['removed_records']}")
    print(f"Success rate: {(stats['cleaned_records']/stats['total_records']*100):.1f}%")
    
    if cleaned_data:
        print(f"\nSample cleaned record:")
        print(json.dumps(cleaned_data[0], indent=2))
    print("="*50)
    
    return True


def main():
    """Main function."""
    print("🧘 YOGA POSES DATASET CLEANER")
    print("="*50)
    
    input_file = "dataset/yoga_sequencing.json"
    output_file = "dataset/cleaned_yoga_poses_simple.json"
    
    success = clean_yoga_dataset(input_file, output_file)
    
    if success:
        print("\n🎉 Data cleaning completed successfully!")
        print("\nTo use with Qdrant:")
        print("1. Install dependencies: pip install qdrant-client sentence-transformers")
        print("2. Start Qdrant: docker run -p 6333:6333 qdrant/qdrant")
        print("3. Use the qdrant_integration.py script to insert data")
    else:
        print("\n💥 Data cleaning failed!")
    
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
