version: 2

sources:
  - name: bronze
    description: Raw ecommerce events
    database: iceberg
    schema: ecommerce
    tables:
      - name: ecommerce_events
        description: Raw ecommerce events
        columns:
          - name: event_id
            description: Event ID
            tests:
              - not_null
              - unique
          - name: user_id
            description: User ID
            tests:
              - not_null
          - name: artist_id
            description: Artist ID
            tests:
              - not_null
          - name: artist_name
            description: Artist Name
            tests:
              - not_null
          - name: song_id
            description: Song ID
            tests:
              - not_null
          - name: song_name
            description: Song Name
            tests:
              - not_null
          - name: song_year
            description: Song Year
            tests:
              - not_null
          - name: event_type
            description: Event Type
            tests:
              - not_null
          - name: device
            description: Device
            tests:
              - not_null
          - name: country
            description: Country
            tests:
              - not_null
          - name: timestamp
            description: Timestamp
            tests:
              - not_null
