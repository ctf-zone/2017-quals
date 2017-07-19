<?php
use Zend\Session\Storage\SessionArrayStorage;
use Zend\Session\Validator\RemoteAddr;
use Zend\Session\Validator\HttpUserAgent;


/**
 * Global Configuration Override
 *
 * You can use this file for overriding configuration values from modules, etc.
 * You would place values in here that are agnostic to the environment and not
 * sensitive to security.
 *
 * @NOTE: In practice, this file will typically be INCLUDED in your source
 * control, so do not include passwords or other sensitive information in this
 * file.
 */

return [
    // 'session' => [
    //     'use_cookies' => true,
    //     'cookie_httponly' => true,
    // ],
    'session_config' => [
        'cookie_lifetime' => 60*60*1,     
        'gc_maxlifetime'     => 60*60*24*30, 
    ],
    'session_storage' => [
        'type' => SessionArrayStorage::class
    ],
    'db' => [
        'driver'    => 'Pdo',
        'dsn'       => "pgsql:host=127.0.0.1;dbname=task200",
        'username'  => 'task200',
        'password'  => 'rahPhila7ud1th',
    ],
    'service_manager' => [
        'factories' => [
            'Zend\Db\Adapter\Adapter'
                    => 'Zend\Db\Adapter\AdapterServiceFactory',
        ],
    ],
    'session_manager' => [
        // Session validators (used for security).
        'validators' => [
            RemoteAddr::class,
            HttpUserAgent::class,
        ]
    ],
    'session_containers' => [
        'ContainerNamespace'
    ],
];
